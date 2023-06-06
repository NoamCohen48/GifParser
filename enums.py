from enum import Enum, IntEnum, auto


class DisposalMethod(IntEnum):
    NotSpecified = 0
    Keep = 1
    ChangeToBackground = 2
    RevertToPrevious = 3
    Undefined = 4
    NONE = -1  # None of the above

    @classmethod
    def _missing_(cls, value):
        if value in range(4, 7):
            return cls.Undefined
        return cls.NONE


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
