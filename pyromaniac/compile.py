from typing import Any
from pathlib import PosixPath as Path

from .remote import Remote
from .compiler import Compiler


def compile(
    source: str, remote: Remote, path: str = "",
    args: tuple = tuple(), kwargs: dict[str, Any] = {},
    parse_args: bool = False,
) -> str:
    """Compile config to ingnition.

    :param source: pyromaniac config source text
    :param remote: remote object with address and authentication secret
    :param path: dot-separated path for library view
    :param args: positional arguments to pass to the component
    :param kwargs: keyword arguments to pass to the component
    :param parse_args: parse args as command line arguments
    :returns: compiled ignition config
    """
    compiler = Compiler.create(Path("."))
    return compiler.compile(source, remote, path, args, kwargs, parse_args)
