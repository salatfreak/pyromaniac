from ..errors import PyromaniacError


class CompilerError(PyromaniacError):
    pass


class NotAComponentError(CompilerError):
    pass


class RenderError(CompilerError):
    pass


class ButaneError(RenderError):
    def __init__(self, message: str):
        self.message = message
