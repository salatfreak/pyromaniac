from types import EllipsisType

from .url import URL


class Pyromaniac:
    def __init__(self, address: tuple[str, str, int], auth: str | None):
        self.address = address
        self.auth = auth

    @property
    def url(self) -> URL:
        return URL(f"{self.address[0]}://{self.address[1]}:{self.address[2]}")

    def remote(
        self, url: str | URL | EllipsisType = ...,
        auth: str | None | EllipsisType = ...,
    ) -> dict:
        url = url if url is not ... else self.url / "config.ign"
        auth = auth if auth is not ... else self.auth
        replace = {'source': url}
        if auth is not None:
            header = {'name': "Authorization", 'value': f"Basic {auth}"}
            replace['http_headers'] = [header]
        return {'ignition.config.replace': replace}
