import logging

import dearpygui.dearpygui as dpg

from .graph_abc import Edge, Node

logger = logging.getLogger("GUI.MathNodes")


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


class DivideNode(Node):
    def __init__(
        self,
        label: str = "Divide",
        is_inspect=False,
        **kwargs,
    ):
        super().__init__(label, is_inspect, **kwargs)
        if not self.settings:
            self.settings = {"numerator": 1, "denominator": 1, "value": 1}

    def setup_attributes(self):
        self.float_output_attribute = self.add_attribute(
            label="Float",
            attribute_type=dpg.mvNode_Attr_Output,
            attribute_style=dpg.mvNode_PinShape_TriangleFilled,
        )
        self.numerator_in = self.add_attribute(
            label="Numerator In",
            attribute_type=dpg.mvNode_Attr_Input,
            attribute_style=dpg.mvNode_PinShape_TriangleFilled,
        )
        self.denominator_in = self.add_attribute(
            label="Denominator In",
            attribute_type=dpg.mvNode_Attr_Input,
            attribute_style=dpg.mvNode_PinShape_TriangleFilled,
        )
        if self.visual_mode:
            self.value = dpg.add_text(
                "N/A",
                parent=self.float_output_attribute,
            )
            self.numerator = dpg.add_text(
                "N/A",
                parent=self.numerator_in,
            )
            self.denominator = dpg.add_text(
                "N/A",
                parent=self.denominator_in,
            )

    def update_settings(self):
        if self.input_attributes[self.numerator_in]:
            edge = self.input_attributes[self.numerator_in][0]
            if edge.data:
                self.settings["numerator"] = edge.data
            else:
                self.settings["numerator"] = None
        if self.input_attributes[self.denominator_in]:
            edge = self.input_attributes[self.denominator_in][0]
            if edge.data:
                self.settings["denominator"] = edge.data
            else:
                self.settings["denominator"] = None

        if self.settings["numerator"] and self.settings["denominator"]:
            self.settings["value"] = (
                self.settings["numerator"] / self.settings["denominator"]
            )
        else:
            self.settings["value"] = None

        if self.visual_mode:
            dpg.set_value(self.numerator, self.settings["numerator"])
            dpg.set_value(self.denominator, self.settings["denominator"])
            dpg.set_value(self.value, self.settings["value"])

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
        value = self.settings["value"]
        for edge in self.output_attributes[self.float_output_attribute]:
            edge.data = value
            logger.debug(f"Populated edge {edge.id} with image from {self.id}")
