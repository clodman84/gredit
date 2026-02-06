import logging

import dearpygui.dearpygui as dpg

from Application import Image, average_brightness

from .graph_abc import Node

logger = logging.getLogger("GUI.EnhanceNodes")


class FloatOut(Node):
    def __init__(
        self,
        label: str = "Float Output",
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


class SimpleAnalysis(Node):
    def __init__(
        self,
        label: str,
        is_inspect=True,
        analysis=lambda: None,
        **kwargs,
    ):
        super().__init__(label, is_inspect, **kwargs)
        self.analysis = analysis

    def setup_attributes(self):
        self.image_attribute = self.add_attribute(
            label="Image", attribute_type=dpg.mvNode_Attr_Input
        )
        self.float_output_attribute = self.add_attribute(
            label="Float",
            attribute_type=dpg.mvNode_Attr_Output,
            attribute_style=dpg.mvNode_PinShape_TriangleFilled,
        )
        if self.visual_mode:
            self.value = dpg.add_text(
                "N/A",
                parent=self.float_output_attribute,
            )

    def update_settings(self):
        pass

    def process(self, is_final=False):
        super().process(is_final=is_final)
        value = None
        if self.input_attributes[self.image_attribute]:
            edge = self.input_attributes[self.image_attribute][0]
            image: Image = edge.data
            if image:
                value = self.analysis(image.raw_image)
                if self.visual_mode:
                    dpg.set_value(self.value, value)

        for edge in self.output_attributes[self.float_output_attribute]:
            edge.data = value
            logger.debug(f"Populated edge {edge.id} with value from {self.id}")


class AverageBrightness(SimpleAnalysis):
    def __init__(
        self,
        label="Average Brightness",
        is_inspect=True,
        analysis=average_brightness,
        **kwargs,
    ):
        super().__init__(label, is_inspect, analysis, **kwargs)
