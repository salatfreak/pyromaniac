from typing import Any

from ..errors import PyromaniacError


class CompilerError(PyromaniacError):
    pass


class NonExistentPathError(CompilerError, AttributeError):
    pass


class NotAComponentError(CompilerError):
    pass


class RenderError(CompilerError):
    pass


class NotADictError(RenderError):
    def __init__(self, result: Any):
        self.result = result


class ButaneError(RenderError):
    def __init__(self, message: str):
        self.message = message
