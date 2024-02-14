from typing import Callable, Any
import ssl
from http.server import BaseHTTPRequestHandler, HTTPServer
from base64 import b64encode
import re
from getpass import getpass

from .log import log
from ..server import certs

SECRET_PATH_RE = re.compile(r'/([a-z0-9-]+)\.secret')


class Server(HTTPServer):
    """HTTP(S) server for ignitions configs and secrets"""

    def __init__(
        self, scheme: str, host: str, auth: str | None,
        generator: Callable[[], str],
    ):
        super().__init__(('0.0.0.0', 8000), self.handle)

        if scheme == 'https':
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(*certs.server(host))
            self.socket = context.wrap_socket(self.socket, server_side=True)

        self.scheme = scheme
        self.host = host
        self.auth = auth
        self.generator = generator

    def handle(self, *args: Any, **kwargs: Any) -> 'Handler':
        return Handler(self.auth, self.generator, *args, **kwargs)


class Handler(BaseHTTPRequestHandler):
    def __init__(
        self, auth: str | None, generator: Callable[[], str], *args, **kwargs
    ):
        self.auth = auth
        self.generator = generator

        super().__init__(*args, **kwargs)

    def do_GET(self):
        if not self.authorized(self.headers.get('Authorization')):
            log("received unauthorized request")
            return self.respond("unauthorized", status=401)

        # serve config from generator
        if self.path == '/config.ign':
            log("compiling and serving config")
            self.respond_headers("application/json")
            config = self.generator()
            return self.respond_body(config)

        # serve secret from prompt
        match = SECRET_PATH_RE.fullmatch(self.path)
        if match:
            log(f'serving secret "{match[1]}"')
            self.respond_headers()
            secret = getpass("Secret: ")
            return self.respond_body(secret)

        # respond with 404
        log("non-existent path requested")
        self.respond("not found", status=404)

    def authorized(self, auth_header: str | None) -> bool:
        if self.auth is None:
            return True
        return auth_header == f"Basic {b64encode(self.auth.encode()).decode()}"

    def respond(self, content, **headers):
        self.respond_headers(**headers)
        if content is not None:
            self.respond_body(content)

    def respond_headers(self, typ='text/plain', status=200):
        self.send_response(status)
        self.send_header('Content-Type', typ)
        self.end_headers()

    def respond_body(self, content):
        if isinstance(content, str):
            content = content.encode()
        self.wfile.write(content)

    # disable potentially insecure logging
    def log_message(self, *args: Any, **kwargs: Any): pass
