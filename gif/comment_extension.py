from attrs import define, field


@define
class CommentExtension:
    data: bytes = field(default=None)
