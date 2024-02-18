from tokenize import TokenInfo


class Token:
    """Syntactic token with source code position.

    :param info: TokenInfo object
    :param slice: position of token in source code
    """

    def __init__(self, info: TokenInfo, slice: slice):
        self.info = info
        self.slice = slice

    @property
    def type(self) -> int:
        """Shortcut for token info type."""
        return self.info.type

    @property
    def string(self) -> str:
        """Shortcut for token info string."""
        return self.info.string

    @property
    def start(self) -> int:
        """Shortcut for source code position start."""
        return self.slice.start

    @property
    def stop(self) -> int:
        """Shortcut for source code position stop."""
        return self.slice.stop
