from typing import TYPE_CHECKING
from ..errors import CodeError

if TYPE_CHECKING:
    from .token import Token


class SegmentError(CodeError):
    """Base class for component code segmenting errors.

    :param token: token at which error occured
    """

    def __init__(self, token: 'Token'):
        super().__init__()
        self.token = token

    @property
    def line(self) -> int:
        """Shortcut for token info start line."""
        return self.token.info.start[0]


class SignatureSyntaxError(SegmentError):
    """Error raised when component signature has unmatched delimiter."""

    def message(self) -> str:
        return f"Unmatched delimiter in signature in line {self.line}."


class UnexpectedTokenError(SegmentError):
    """Error raised when invalid token is encountered while segmentating code.

    :param token: token at wich error occured
    :param location: string describing where the error occured
    """

    def __init__(self, token: 'Token', location: str):
        super().__init__(token)
        self.location = location

    def message(self) -> str:
        string = repr(self.token.string)
        return f"Unexpected {string} {self.location} in line {self.line}."
