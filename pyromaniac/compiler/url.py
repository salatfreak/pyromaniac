from typing import Self, Any


class URL:
    """URL type.

    :param url: URL as string or URL object
    """

    def __init__(self, url: str | Self):
        self.url = url.url if isinstance(url, URL) else url

    def __truediv__(self, path: str) -> Self:
        """Concatenation path to URL with slash syntax.

        :param path: path string to be concatenated
        :returns: concatenated URL object
        """
        return URL(f"{self}/{path}")

    def __str__(self) -> str:
        return self.url

    def __repr__(self) -> str:
        return f"URL({repr(self.url)})"

    def __eq__(self, other: Any) -> bool:
        return type(self) is type(other) and self.url == other.url
