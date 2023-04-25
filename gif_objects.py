from typing import Any

from PIL import Image as Image_PIL
from attrs import define, field, Factory


@define
class ApplicationExtension:
    application_name: str = field(default=None)
    identify: str = field(default=None)
    data: str = field(default=None)


@define
class GraphicControlExtension:
    disposal: int = field(default=None)
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
    text_color: str = field(default=None)
    text_data: str = field(default=None)


@define
class Image:
    top: int = field(default=None)
    left: int = field(default=None)
    width: int = field(default=None)
    height: int = field(default=None)

    interlace_index: int = field(default=None)
    local_color_table_flag: bool = field(default=None)
    graphic_control_extension_index: int = field(default=None)
    background_color_index: int = field(default=None)
    size_of_local_color_table: int = field(default=None)
    image_data: list[Any] = field(factory=list, repr=False)
    image_indexes: list[Any] = field(factory=list, repr=False)
    # we think we don't need it
    local_color_table_index: int = field(default=None)
    plain_text_extension_index: int = field(default=None)
    img: Image_PIL = field(default=None)


@define
class Gif:
    version: str = field(default=None)
    width: int = field(default=None)
    height: int = field(default=None)

    global_color_table_size: int = field(default=None)
    global_color_table: Image_PIL = field(default=None, repr=False)
    background_color_index: int = field(default=None)
    images: list[Image] = field(factory=list, repr=False)
    applications_extensions: list[ApplicationExtension] = field(factory=list, repr=False)
    graphic_control_extensions: list[GraphicControlExtension] = field(factory=list, repr=False)
    plain_text_extensions: list[PlainTextExtension] = field(factory=list, repr=False)
    local_color_tables: list[Image_PIL] = field(factory=list, repr=False)

    def add_application_extension(self, extension):
        self.applications_extensions.append(extension)


class IncorrectFileFormat(Exception):
    def __init__(self, message):
        super().__init__(message)
