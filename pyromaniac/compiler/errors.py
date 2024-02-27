from ..errors import PyromaniacError


class CompilerError(PyromaniacError):
    pass


class RenderError(CompilerError):
    pass


class NotAComponentError(CompilerError):
    pass
