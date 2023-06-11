from enum import Enum


class BlockPrefix(Enum):
    ImageDescriptor = b'\x2C'
    Extension = b'\x21'
    GraphicControlExtension = b'\xF9'
    CommentExtension = b'\xFE'
    PlainTextExtension = b'\x01'
    ApplicationExtension = b'\xFF'
    Terminator = b'\x00'
    Trailer = b'\x3b'
    NONE = b''  # None of the above

    @classmethod
    def _missing_(cls, value):
        return cls.NONE
