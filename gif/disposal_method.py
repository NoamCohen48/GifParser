from enum import IntEnum


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
