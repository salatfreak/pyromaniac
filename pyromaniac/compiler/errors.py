class CompilerError(Exception):
    pass


class RenderError(CompilerError):
    pass


class NotAComponentError(CompilerError):
    pass
