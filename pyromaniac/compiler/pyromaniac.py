from .url import URL


class Pyromaniac:
    def __init__(self, address: tuple[str, str, int], auth: str | None):
        self.address = address
        self.auth = auth

    @property
    def url(self) -> URL:
        return URL(f"{self.address[0]}://{self.address[1]}:{self.address[2]}")
