from attrs import define, field


@define
class GraphicControlExtension:
    disposal: int = field(default=None)
    reserved: int = field(default=None)
    user_input_flag: bool = field(default=None)
    transparent_color_flag: int = field(default=None)
    transparent_index: int = field(default=None)
    delay_time: int = field(default=None)
