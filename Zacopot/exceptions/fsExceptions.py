
class DirNotFoundException(Exception):
    __slots__ = "message"

    def __init__(self, message):
        self.message = message
        super().__init__(message)


class CannotOpenDirException(Exception):
    __slots__ = "message"

    def __init__(self, message):
        self.message = message
        super().__init__(message)


class BlockSizeExceededException(Exception):
    __slots__ = "message"

    def __init__(self, message):
        self.message = message
        super().__init__(message)
