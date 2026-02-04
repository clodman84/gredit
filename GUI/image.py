import logging

import dearpygui.dearpygui as dpg

from Application import ImageManager
from Application.utils import ShittyMultiThreading
from Gredit.image_editor import EditingWindow

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

            with dpg.group(horizontal=True) as self.ribbon:
                dpg.add_button(label="Next", callback=self.next)
                dpg.add_button(label="Previous", callback=self.previous)
                dpg.add_slider_int(
                    default_value=1,
                    min_value=1,
                    max_value=self.image_manager.end_index,
                    callback=lambda _, a, u: self.open(a - 1),
                    tag=f"{self.parent}_Image Slider",
                )
                dpg.add_button(
                    label="Edit",
                    callback=lambda: EditingWindow(
                        self.image_manager.load(self.current_image),
                        on_close=lambda: self.open(
                            self.current_image, force_reload=True
                        ),
                    ),
                )

            with dpg.group(horizontal=False):
                dpg.add_image(f"{self.parent}_Main Image")

    def open(self, index: int, force_reload=False):
        self.current_image = index
        image = self.image_manager.load(index, force_reload=force_reload)
        dpg.set_value(f"{self.parent}_Main Image", image.dpg_texture)
        dpg.set_value(f"{self.parent}_Image Slider", self.current_image + 1)

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
