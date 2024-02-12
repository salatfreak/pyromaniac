from typing import Self

from ..errors import CompilerError
from .keys import format


class KeyExpandError(CompilerError):
    """Key expand error.

    :param parts: list of key parts
    """

    def __init__(self, parts: list[str | int] = []):
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


class DuplicateKeyError(KeyExpandError):
    pass


class MixedKeysError(KeyExpandError):
    pass


class MissingIndexError(KeyExpandError):
    pass
