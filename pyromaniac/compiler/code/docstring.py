import ast

from .errors import InvalidDocstringError


def parse(code: str) -> str:
    # parse doc string source code
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        raise InvalidDocstringError() from e

    # extract string content
    if not len(tree.body) == 1 \
            or not isinstance(tree.body[0], ast.Expr) \
            or not isinstance(tree.body[0].value, ast.Constant) \
            or not isinstance(tree.body[0].value.value, str):
        raise InvalidDocstringError()

    # return string content
    return tree.body[0].value.value
