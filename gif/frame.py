import typing

from PIL.Image import Image
from attrs import define, field


@define
class Frame:
    image_data: list[bytes] = field(factory=list, repr=False)
    raw_data: list[bytes] = field(factory=list, repr=False)
    raw_indexes: bytes = field(factory=bytes, repr=False)
    image_indexes: list[typing.Any] = field(factory=list, repr=False)

    top: int = field(default=None)
    left: int = field(default=None)
    width: int = field(default=None)
    height: int = field(default=None)

    reset_size: int = field(default=None)
    interlace_flag: bool = field(default=None)
    sort_flag: bool = field(default=None)
    reserved: int = field(default=None)
    local_color_table_flag: bool = field(default=None)
    background_color_index: int = field(default=None)
    size_of_local_color_table: int = field(default=None)

    img: Image = field(default=None)

    local_color_table: list[bytes] = field(default=None)
    lzw_minimum_code_size: int = field(default=None)

    index_graphic_control_ex: int | None = field(default=None)
