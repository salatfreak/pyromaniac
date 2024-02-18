from typing import TYPE_CHECKING
from ..errors import CodeError

if TYPE_CHECKING:
    from .token import Token


class SegmentError(CodeError):
    """Code segmenting error.

    :param token: token at which error occured
    """

    def __init__(self, token: 'Token'):
        self.token = token

    @property
    def line(self) -> int:
        """Shortcut for token info start line."""
        return self.token.info.start[0]


class InvalidSignatureError(SegmentError):
    """Invalid signature error.

    :param token: token at wich error occured
    """

    def __str__(self) -> str:
        print(self.token.string)
        return f"unmatched delimiter in signature in line {self.line}"


class UnexpectedTokenError(SegmentError):
    """Unexpected token error.

    :param token: token at wich error occured
    :param location: string describing where the error occured
    """

    def __init__(self, token: 'Token', location: str):
        super().__init__(token)
        self.location = location

    def __str__(self) -> str:
        string = repr(self.token.string)
        return f"unexpected {string} {self.location} in line {self.line}"
