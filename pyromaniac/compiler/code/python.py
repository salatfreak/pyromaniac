from typing import Self
import ast

from ..errors import CompilerError
from .errors import PythonSyntaxError, PythonRuntimeError


class Python:
    """Component python code."""

    def __init__(self, code: str):
        self.code = code

    @classmethod
    def create(cls, code: str, pure: bool) -> Self:
        """Create component python code and check syntax.

        Modifies python code to store result of trailing expression in variable
        named *result* if a pure python component.

        :param code: component python source code
        :param last: whether is pure python component
        :returns: constructed component python code object
        """
        if pure:
            code = add_assignment(code)
        else:
            check_syntax(code)

        return cls(code)

    def execute(self, context: dict):
        """Execute component python code in given context.

        All fields from the context will be avaiable to the python code and all
        names assigned inside the code will be writte into the context.

        In pure python components the result of the trailing expression will be
        stored in the contexts *result* field if no error occurs.

        :param context: context to execute code in
        """
        try:
            exec(self.code, context)
            del context['__builtins__']
        except CompilerError as e:
            raise e
        except Exception as e:
            raise PythonRuntimeError() from e


def check_syntax(code: str):
    try:
        ast.parse(code)
    except SyntaxError as e:
        raise PythonSyntaxError() from e


def add_assignment(code: str) -> str:
    # parse component
    try:
        mod = ast.parse(code)
    except SyntaxError as e:
        raise PythonSyntaxError() from e

    # check for trailing expression
    if len(mod.body) == 0 or not isinstance(mod.body[-1], ast.Expr):
        raise PythonSyntaxError.end_expression()
    expr = mod.body[-1]

    # insert assignment
    lines = code.splitlines()
    line = lines[expr.lineno - 1]
    line = line[:expr.col_offset] + "result=" + line[expr.col_offset:]
    lines[expr.lineno - 1] = line

    # return transformed code string
    return "\n".join(lines)
