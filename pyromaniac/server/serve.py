from typing import Callable

from .log import log
from .server import Server


def serve(
    generator: Callable[[], str],
    scheme: str, host: str, auth: str | None = None,
):
    """Serve config and secrets until keyboard interrupt.

    Serves the ignition config produced by `generator()` under "/config.ign"
    and secrets under "/NAME.secret" from prompting on tty. Uses host and port
    for generating TLS certificate. No authentication is used when auth is
    None.

    :param generator: function that generates an ignition config
    :param scheme: http or https
    :param host: host name or ip address for connection securing
    :param auth: optional credentials in the format "USER:PASS"
    """

    # run server
    log("starting server")
    server = Server(scheme, host, auth, generator)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
    log("server stopped")
