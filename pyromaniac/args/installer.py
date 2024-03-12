from typing import Callable
from collections.abc import Iterable
from argparse import SUPPRESS


ARGS = [
    ("dest-ignition", 1),
    ("dest-device", 1),
    ("dest-console", 1),
    ("dest-karg-append", 1),
    ("dest-karg-delete", 1),
    ("network-keyfile", 1),
    ("network-nmstate", 1),
    ("ignition-ca", 1),
    ("pre-install", 1),
    ("post-install", 1),
    ("installer-config", 1),
    ("live-ignition", 1),
    ("live-karg-append", 1),
    ("live-karg-delete", 1),
    ("live-karg-replace", 1),
    ("force", 0),
    ("output", 1),
    ("help", 0),
]


def generate() -> Iterable[tuple[list[str], dict[str, str]]]:
    """Generate arguments for coreos-installer.

    Generates tuples and dicts of values for add_argument() for passing through
    values to the coreos-installer.
    """
    for name, arg_count in ARGS:
        args = [f"--iso-raw-{name}"]
        kwargs = {'dest': 'installer', 'default': [], 'help': SUPPRESS}
        match arg_count:
            case 0: kwargs.update({'action': 'append_const', 'const': (name,)})
            case 1: kwargs.update({'action': 'append', 'type': wrap(name)})
        yield args, kwargs


def wrap(name: str) -> Callable[[str], tuple[str, str]]:
    return lambda value: (name, value)
