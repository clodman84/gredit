import logging

import dearpygui.dearpygui as dpg
from PIL import ImageEnhance

from Application import Image, multiply

from .graph_abc import Edge, Node

logger = logging.getLogger("GUI.EnhanceNodes")


class EnhanceNode(Node):
    def __init__(
        self,
        label: str,
        is_inspect=False,
        enhancement=lambda: None,
        **kwargs,
    ):
        super().__init__(label, is_inspect, **kwargs)
        if not self.settings:
            self.settings = {"value": 1}
        self.enhancement = enhancement

    def setup_attributes(self):
        self.image_attribute = self.add_attribute(
            label="Image", attribute_type=dpg.mvNode_Attr_Input
        )
        self.image_output_attribute = self.add_attribute(
            label="Out", attribute_type=dpg.mvNode_Attr_Output
        )
        self.float_input_attribute = self.add_attribute(
            label="Float",
            attribute_type=dpg.mvNode_Attr_Input,
            attribute_style=dpg.mvNode_PinShape_TriangleFilled,
        )

        if self.visual_mode:
            self.slider = dpg.add_input_float(
                parent=self.image_attribute,
                default_value=self.settings["value"],
                callback=self.update,
                width=200,
            )

    def update_settings(self):
        if self.input_attributes[self.float_input_attribute]:
            edge = self.input_attributes[self.float_input_attribute][0]
            if edge.data:
                self.settings["value"] = edge.data
                if self.visual_mode:
                    dpg.set_value(self.slider, edge.data)
            return

        if self.visual_mode:
            self.settings["value"] = dpg.get_value(self.slider)

    def validate_input(self, edge: Edge, attribute_id) -> bool:
        # only permitting a single connection
        if self.input_attributes[edge.output_attribute_id]:
            logger.warning(
                "Invalid! You can only connect one image node to enhance node"
            )
            return False
        return True

    def process(self, is_final=False):
        super().process(is_final=is_final)
        if self.input_attributes[self.image_attribute]:
            edge = self.input_attributes[self.image_attribute][0]
            image: Image = edge.data
            if image:
                enhancer = self.enhancement(image.raw_image)
                factor = self.settings["value"]
                updated_image = enhancer.enhance(factor=factor)
                image = Image(image.path, updated_image, (600, 600), (200, 200))

            for edge in self.output_attributes[self.image_output_attribute]:
                edge.data = image
                logger.debug(f"Populated edge {edge.id} with image from {self.id}")


class Saturation(EnhanceNode):
    def __init__(self, enhancement=ImageEnhance.Color, label="Saturation", **kwargs):
        super().__init__(label, enhancement=enhancement, **kwargs)


class Contrast(EnhanceNode):
    def __init__(self, enhancement=ImageEnhance.Contrast, label="Contrast", **kwargs):
        super().__init__(label, enhancement=enhancement, **kwargs)


class Brightness(EnhanceNode):
    def __init__(
        self, enhancement=ImageEnhance.Brightness, label="Brightness", **kwargs
    ):
        super().__init__(label, enhancement=enhancement, **kwargs)


class Multiply(Node):
    def __init__(
        self,
        label="Multiply",
        is_inspect=False,
        **kwargs,
    ):
        super().__init__(label, is_inspect, **kwargs)
        if not self.settings:
            self.settings = {"value": 1}

    def setup_attributes(self):
        self.image_attribute = self.add_attribute(
            label="Image", attribute_type=dpg.mvNode_Attr_Input
        )
        self.image_output_attribute = self.add_attribute(
            label="Out", attribute_type=dpg.mvNode_Attr_Output
        )
        self.float_input_attribute = self.add_attribute(
            label="Float",
            attribute_type=dpg.mvNode_Attr_Input,
            attribute_style=dpg.mvNode_PinShape_TriangleFilled,
        )

        if self.visual_mode:
            self.slider = dpg.add_input_float(
                parent=self.image_attribute,
                default_value=self.settings["value"],
                callback=self.update,
                width=200,
            )

    def update_settings(self):
        if self.input_attributes[self.float_input_attribute]:
            edge = self.input_attributes[self.float_input_attribute][0]
            if edge.data:
                self.settings["value"] = edge.data
                if self.visual_mode:
                    dpg.set_value(self.slider, edge.data)
            return

        if self.visual_mode:
            self.settings["value"] = dpg.get_value(self.slider)

    def validate_input(self, edge: Edge, attribute_id) -> bool:
        # only permitting a single connection
        if self.input_attributes[edge.output_attribute_id]:
            logger.warning(
                "Invalid! You can only connect one image node to enhance node"
            )
            return False
        return True

    def process(self, is_final=False):
        super().process(is_final=is_final)
        if self.input_attributes[self.image_attribute]:
            edge = self.input_attributes[self.image_attribute][0]
            image: Image = edge.data
            if image:
                updated_image = multiply(image.raw_image, self.settings["value"])
                image = Image(image.path, updated_image, (600, 600), (200, 200))

            for edge in self.output_attributes[self.image_output_attribute]:
                edge.data = image
                logger.debug(f"Populated edge {edge.id} with image from {self.id}")
