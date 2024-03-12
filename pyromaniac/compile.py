from typing import Any
from pathlib import PosixPath as Path

from .remote import Remote
from .compiler import Compiler


def compile(
    source: str, remote: Remote,
    args: tuple = tuple(), kwargs: dict[str, Any] = {},
) -> str:
    """Compile config to ingnition.

    :param source: pyromaniac config source text
    :param remote: remote object with address and authentication secret
    :param args: positional arguments to pass to the component
    :param kwargs: keyword arguments to pass to the component
    :returns: compiled ignition config
    """
    compiler = Compiler.create(Path("."))
    return compiler.compile(source, remote, args, kwargs)
