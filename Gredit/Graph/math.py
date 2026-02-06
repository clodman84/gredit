import logging

import dearpygui.dearpygui as dpg

from Application import Image

from .graph_abc import Node

logger = logging.getLogger("GUI.EnhanceNodes")


class MathNode(Node):
    def __init__(
        self,
        label: str = "Math",
        is_inspect=False,
        **kwargs,
    ):
        super().__init__(label, is_inspect, **kwargs)
        if not self.settings:
            self.settings = {"value": 1}

    def setup_attributes(self):
        self.float_output_attribute = self.add_attribute(
            label="Float",
            attribute_type=dpg.mvNode_Attr_Output,
            attribute_style=dpg.mvNode_PinShape_TriangleFilled,
        )
        if self.visual_mode:
            self.slider = dpg.add_input_float(
                parent=self.float_output_attribute,
                default_value=self.settings["value"],
                callback=self.update,
                width=200,
            )

    def update_settings(self):
        if self.visual_mode:
            self.settings["value"] = dpg.get_value(self.slider)

    def process(self, is_final=False):
        super().process(is_final=is_final)
        for edge in self.output_attributes[self.float_output_attribute]:
            edge.data = self.settings["value"]
            logger.debug(f"Populated edge {edge.id} with image from {self.id}")
