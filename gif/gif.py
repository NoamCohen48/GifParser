import typing

from attrs import define, field

from .application_extension import ApplicationExtension
from .comment_extension import CommentExtension
from .frame import Frame
from .graphic_control_extension import GraphicControlExtension
from .plain_text_extension import PlainTextExtension


@define
class Gif:
    structure: list[typing.Any] = field(factory=list, repr=False)
    images: list[Frame] = field(factory=list, repr=False)
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
