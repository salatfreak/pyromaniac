from typing import Any
from pathlib import PosixPath as Path

from .compiler import Compiler


def compile(
    source: str, address: tuple[str, str, int], auth: str | None = None,
    args: list = [], kwargs: dict[str, Any] = {},
) -> str:
    """Compile config to ingnition.

    :param source: pyromaniac config source text
    :param address: scheme, host and port for encryption secret requests
    :param auth: basic auth credentials for encryption secret reqeusts
    :param args: positional arguments to pass to the component
    :param kwargs: keyword arguments to pass to the component
    :returns: compiled ignition config
    """
    compiler = Compiler.create(Path("."))
    return compiler.compile(source, address, auth, args, kwargs)
