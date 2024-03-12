from argparse import Namespace

from .parser import parser


def parse(args: list[str] | None = None) -> Namespace:
    """Parse command line arguments.

    :param args: arguments to parse instead of command line arguments
    :returns: representation of the parsed arguments
    """
    namespace = parser.parse_args(args)
    return namespace
