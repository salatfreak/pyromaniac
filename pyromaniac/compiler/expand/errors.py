from typing import Self

from ..errors import CompilerError
from .keys import format


class KeyExpandError(CompilerError):
    """Base class for dictionary composite key expansion errors.

    :param parts: list of key parts
    """

    def __init__(self, parts: list[str | int] = []):
        super().__init__()
        self.parts = parts

    def under(self, prefix: str | int) -> Self:
        """Construct error with prepended key part.

        :param prefix: part to prepend to key parts
        :returns: new error with prepended key part
        """
        return self.__class__([prefix, *self.parts])

    def key(self) -> str:
        """Format key parts into a single key string.

        :returns: formatted key string
        """
        return format(self.parts)

    def message(self) -> str:
        key = repr(self.key())
        return f"Expanding composite key {key} failed: {self.reason()}"


class DuplicateKeyError(KeyExpandError):
    """Error raised when key was specified twice."""

    def reason(self) -> str:
        return "Key was specified twice."


class MixedKeysError(KeyExpandError):
    """Error raised when string and integer keys are mixed for an element."""

    def reason(self) -> str:
        return "Mixed string and integer keys."


class MissingIndexError(KeyExpandError):
    """Error raised when array keys are not continuous."""

    def reason(self) -> str:
        return "Array index missing."
