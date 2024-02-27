from ..errors import PyromaniacError


class CompilerError(PyromaniacError):
    pass


class NotAComponentError(CompilerError):
    pass


class RenderError(CompilerError):
    pass
