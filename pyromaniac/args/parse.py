from argparse import Namespace

from .types import auth
from .parser import parser


def parse(args: list[str] | None = None) -> Namespace:
    """Parse command line arguments.

    :param args: arguments to parse instead of command line arguments
    :returns: representation of the parsed arguments
    """
    namespace = parser.parse_args(args)
    namespace.auth = auth(namespace.auth, *namespace.address)
    return namespace
