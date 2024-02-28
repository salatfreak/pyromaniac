import re
from pathlib import PosixPath as Path

from ..server.auth import auto_auth

ADDRESS_RE = re.compile("".join([
    r'(?:(http(?:s)?)://)?',
    r'(\[[0-9a-f:]+\]|[0-9.]+|[a-z0-9-.]+)',
    r'(?::([1-9][0-9]*))?',
]))
OptStr = str | None


# type parsers
def net(value: str) -> str:
    # fields names
    fields = [
        "client", "server", "gw", "netmask", "hostname", "device",
        "autoconf", "dns0", "dns1", "ntp0",
    ]

    # apply supplied values
    config = {field: "" for field in fields}
    for assignment in value.split(","):
        if "=" not in assignment or ":" in assignment:
            raise ValueError(f'invalid value assignment "{assignment}"')
        k, v = (s.strip() for s in assignment.split("=", 1))
        if k not in config:
            raise ValueError(f'unknown keyword "{k}"')
        config[k] = v

    # assemble configuration string
    return ":".join(config[d] for d in fields)


def address(value: str) -> tuple[str, str, int]:
    match = ADDRESS_RE.fullmatch(value.lower().rstrip("/"))
    if not match:
        raise ValueError(f'invalid address "{value}"')

    scheme = match[1] or "http"
    host = match[2]
    port = int(match[3] or {"https": 443, "http": 80}[scheme])

    return scheme, host, port


def auth(value: str, scheme: str, host: str, port: int) -> str | None:
    if value == 'default':
        value = {"http": 'none', "https": 'auto'}[scheme]

    if value == 'none':
        return None
    elif value == 'auto':
        return auto_auth(scheme, host, port)
    else:
        return value


def input(value: str) -> Path:
    path = Path(value)
    return path.joinpath("main.pyro") if path.is_dir() else path
