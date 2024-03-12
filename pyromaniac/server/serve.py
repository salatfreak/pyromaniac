from typing import Callable, TYPE_CHECKING

from .log import log
from .server import Server

if TYPE_CHECKING:
    from ..remote import Remote


def serve(remote: 'Remote', generator: Callable[[], str]):
    """Serve config and secrets until keyboard interrupt.

    Serves the ignition config produced by `generator()` under "/config.ign"
    and secrets under "/NAME.secret" from prompting on tty. Uses host and port
    for generating TLS certificate. No authentication is used when auth is
    None.

    :param remote: remote object with address and authentication secret
    :param generator: function that generates an ignition config
    """

    # run server
    log("starting server")
    server = Server(remote.scheme, remote.host, remote.auth, generator)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
    log("server stopped")
