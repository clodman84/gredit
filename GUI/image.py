import functools
import logging

import dearpygui.dearpygui as dpg

from Application import ImageManager
from Application.utils import ShittyMultiThreading
from Gredit.Graph.graph_abc import Edge, Graph, Node
from Gredit.Graph.image_nodes import ImageNode
from Gredit.image_editor import EditingWindow, load_graph_window

logger = logging.getLogger("GUI.Image")


class ImageWindow:
    """imej"""

    def __init__(
        self,
        roll: str,
        image_manager: ImageManager,
        main_image_dimensions,
        thumnail_dimensions,
        window_dimensions,
    ):
        self.current_image: int = 0
        self.roll = roll

        self.image_manager = image_manager

        self.main_image_dimensions = main_image_dimensions
        self.thumnail_dimensions = thumnail_dimensions
        self.window_dimensions = window_dimensions

        with dpg.window(
            label=self.roll,
            width=self.window_dimensions[0],
            height=self.window_dimensions[1],
        ) as self.parent:
            self.setup()
        self.image_manager.load_in_background()

    def setup(self):
        logger.debug("Setting Up Image Window")
        with dpg.child_window():
            # this is an abomination, but it makes the window load 2 seconds faster
            ShittyMultiThreading(
                self.image_manager.load, (0, 1, self.image_manager.end_index - 1)
            ).start()

            image = self.image_manager.load(0)
            logger.debug(image.dpg_texture.shape)
            with dpg.texture_registry():
                # TODO: The next and previous image viewer could be changed into a scrollable selector
                # with all the images in them
                dpg.add_dynamic_texture(
                    *self.main_image_dimensions,
                    default_value=image.dpg_texture,
                    tag=f"{self.parent}_Main Image",
                )
            with dpg.menu_bar(parent=self.parent):
                dpg.add_menu_item(label="Previous", callback=self.previous)
                dpg.add_menu_item(label="Next", callback=self.next)
                with dpg.menu(label="Edit"):
                    dpg.add_menu_item(
                        label="Open Graph",
                        callback=lambda: EditingWindow(
                            self.image_manager.load(self.current_image),
                            on_close=lambda: self.open(
                                self.current_image, force_reload=True
                            ),
                        ),
                    )
                    with dpg.tooltip(dpg.last_item()):
                        dpg.add_text("Edit image in graph editor")

                    dpg.add_menu_item(
                        label="Apply Workflow",
                        callback=lambda: load_graph_window(self.load_graph),
                    )
                    with dpg.tooltip(dpg.last_item()):
                        dpg.add_text("Apply saved workflow to this image")
                    dpg.add_menu_item(
                        label="Apply Workflow to All",
                        callback=lambda: load_graph_window(self.load_graph_all),
                    )
                    with dpg.tooltip(dpg.last_item()):
                        dpg.add_text("Apply saved workflow to all images in folder")

            with dpg.group(horizontal=False):
                self.loading_indicator = dpg.add_loading_indicator()
                dpg.hide_item(self.loading_indicator)
                dpg.add_image(f"{self.parent}_Main Image")
                dpg.add_slider_int(
                    default_value=1,
                    min_value=1,
                    max_value=self.image_manager.end_index,
                    callback=lambda _, a, u: self.open(a - 1),
                    tag=f"{self.parent}_Image Slider",
                    width=self.main_image_dimensions[0],
                )

    def open(self, index: int, force_reload=False):
        self.current_image = index
        image = self.image_manager.load(index, force_reload=force_reload)
        dpg.set_value(f"{self.parent}_Main Image", image.dpg_texture)
        dpg.set_value(f"{self.parent}_Image Slider", self.current_image + 1)

    def load_graph_all(self, filename):
        ShittyMultiThreading(
            functools.partial(self.load_graph, filename),
            range(self.image_manager.end_index),
        ).start()

    def load_graph(self, filename, image_index=None):
        logger.info(f"Processing image: {image_index}")
        graph = Graph()
        if not image_index:
            image_index = self.current_image
        image = self.image_manager.load(image_index)
        for node in graph.load_nodes(filename):
            # ignore your lsp this shit sucks ass I know, but fuck it
            if node.label == "Import":
                node.image = image
            node.setup_attributes()
            graph.add_node(node)
        for edges in graph.load_node_output_attributes(filename=filename):
            for edge in edges:
                input_node = graph.node_lookup_by_uuid[edge["input"]]
                output_node = graph.node_lookup_by_uuid[edge["output"]]
                input_attr = input_node.output_attributes_id_lookup[edge["input_attr"]]
                output_attr = output_node.input_attributes_id_lookup[
                    edge["output_attr"]
                ]
                input: Node = graph.node_lookup_by_attribute_id[input_attr]
                output: Node = graph.node_lookup_by_attribute_id[output_attr]
                made_edge = Edge("a", None, input, output, input_attr, output_attr)
                graph.link(input, output, made_edge)

        dpg.show_item(self.loading_indicator)
        graph.evaluate(is_final=True)
        dpg.hide_item(self.loading_indicator)
        self.open(image_index, force_reload=True)

    def next(self):
        if self.current_image < self.image_manager.end_index - 1:
            self.open(self.current_image + 1)
        else:
            self.open(0)

    def previous(self):
        if self.current_image > 0:
            self.open(self.current_image - 1)
        else:
            self.open(self.image_manager.end_index - 1)
