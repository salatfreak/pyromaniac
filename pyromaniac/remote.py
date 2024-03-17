from typing import Self
from base64 import b64encode

from .server.auth import auto_auth
from .server.certs import root
from .compiler.url import URL


class Remote:
    """Remote server data and merge config generator."""

    def __init__(self, scheme: str, host: str, port: int, auth: str | None):
        self.scheme = scheme
        self.host = host
        self.port = port
        self.__auth = auth

    @classmethod
    def create(
        cls, address: tuple[str, str, int], auth: str | None = None
    ) -> Self:
        """Create Remote object.

        Converts auth string "none" to None, applies default auth value for
        HTTPS scheme and constructs the Remote object.

        :param address: tuple with scheme, address, and port
        :param auth: authentication secret, "none", "auto", or None
        :returns: the constructed Remote object
        """
        match address[0], auth:
            case 'https', None: auth = 'auto'
            case _, 'none': auth = None

        return cls(*address, auth)

    @property
    def auth(self) -> str | None:
        """Get credentials, automatically generating them if configured."""
        if self.__auth == 'auto':
            self.__auth = auto_auth(self.scheme, self.host, self.port)
        return self.__auth

    @property
    def url(self) -> URL:
        """Assemble URL from scheme, host, and port."""
        return URL(f"{self.scheme}://{self.host}:{self.port}")

    @property
    def headers(self) -> dict:
        """Return HTTP headers as dict for authentication."""
        if self.auth is None:
            return {}
        auth = b64encode(self.auth.encode()).decode()
        return {"Authorization": f"Basic {auth}"}

    def __call__(self) -> dict:
        """Generate remote merge configuration.

        Adds the merge source, authorization header if requested and TLS root
        certificate if scheme is "https".

        :returns: pyromaniac config for creating the remote ISO
        """
        result = {'ignition.config.merge[0].source': self.url / "config.ign"}
        if self.auth is not None:
            result['ignition.config.merge[0].http_headers'] = [
                {'name': k, 'value': v} for k, v in self.headers.items()
            ]
        if self.scheme == "https":
            key = 'ignition.security.tls.certificate_authorities[0].inline'
            result[key] = root()[0].read_text()
        return result
