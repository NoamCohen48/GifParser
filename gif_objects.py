import typing

from PIL import Image as Image_PIL
from attrs import define, field


class IncorrectFileFormat(Exception):
    def __init__(self, message):
        super().__init__(message)


@define
class ApplicationExtension:
    application_name: str | None = None
    identify: str | None = None
    data: bytes | None = None


@define
class GraphicControlExtension:
    disposal: int = field(default=None)
    reserved: int = field(default=None)
    user_input_flag: bool = field(default=None)
    transparent_color_flag: int = field(default=None)
    transparent_index: int = field(default=None)
    delay_time: int = field(default=None)


@define
class PlainTextExtension:
    top: int = field(default=None)
    left: int = field(default=None)
    width: int = field(default=None)
    height: int = field(default=None)

    char_width: int = field(default=None)
    char_height: int = field(default=None)
    background_color: int = field(default=None)
    text_color: int = field(default=None)
    data: bytes = field(default=None)


@define
class CommentExtension:
    data: bytes = field(default=None)


@define
class Image:
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

    img: Image_PIL.Image = field(default=None)

    local_color_table: list[bytes] = field(default=None)
    lzw_minimum_code_size: int = field(default=None)

    index_graphic_control_ex: int | None = field(default=None)


@define
class Gif:
    structure: list[typing.Any] = field(factory=list, repr=False)
    images: list[Image] = field(factory=list, repr=False)
    applications_extensions: list[ApplicationExtension] = field(factory=list, repr=False)
    comments_extensions: list[CommentExtension] = field(factory=list, repr=False)
    graphic_control_extensions: list[GraphicControlExtension] = field(factory=list, repr=False)
    plain_text_extensions: list[PlainTextExtension] = field(factory=list, repr=False)
    local_color_tables: list[list[bytes]] = field(factory=list, repr=False)

    version: str = field(default=None)
    width: int = field(default=None)
    height: int = field(default=None)

    global_color_table_size: int = field(default=None)
    color_resolution: int = field(default=None)
    sort_flag: bool = field(default=None)
    global_color_table: list[bytes] = field(default=None, repr=False)
    background_color_index: int = field(default=None)
    pixel_aspect_ratio: float = field(default=None)

    def add_application_extension(self, extension):
        self.applications_extensions.append(extension)
