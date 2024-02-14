from pathlib import PosixPath as Path

from .compiler import Compiler


def compile(
    source: str, address: tuple[str, str, int], auth: str | None = None,
) -> str:
    """Compile config to ingnition.

    :param source: pyromaniac config source text
    :param address: scheme, host and port for encryption secret requests
    :param auth: basic auth credentials for encryption secret reqeusts
    :returns: compiled ignition config
    """
    return Compiler.create(Path(".")).compile(source, address, auth)
