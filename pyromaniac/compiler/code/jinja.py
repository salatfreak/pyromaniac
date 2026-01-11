from typing import Any
from collections.abc import Iterable
from datetime import date, datetime, time
from pathlib import PosixPath as Path
import re
from json import dumps as json_dumps, JSONEncoder as JSONEncoderBase
from jinja2 import Environment

from ..url import URL

SAFE_SHELL_ARG_RE = re.compile(r'^[\w./:+,@=-]+$')


# raw object wrapper
class Raw:
    __match_args__ = ("content",)

    def __init__(self, content: Any):
        self.content = content


# shell escaping filter
def shell(content: Any) -> str:
    if isinstance(content, str | bytes) or not isinstance(content, Iterable):
        content = [content]
    return " ".join(escape_shell_arg(arg) for arg in content)


def escape_shell_arg(arg: str):
    if SAFE_SHELL_ARG_RE.fullmatch(arg):
        return arg
    return "'" + arg.replace("'", r"'\''") + "'"


# ellipsis test
def ellipsis(val: Any) -> bool:
    return val is Ellipsis


# JSON environments
class JSONEncoder(JSONEncoderBase):
    def default(self, o: Any) -> Any:
        match o:
            case Path() | URL():
                return str(o)
            case _:
                return super().default(o)


def json_finalize(obj: Any) -> str:
    match obj:
        case Raw(content):
            return str(content)
        case _:
            return json_dumps(obj, cls=JSONEncoder)


# default environment
default_env = Environment()
default_env.filters['shell'] = shell
default_env.tests['ellipsis'] = ellipsis

# pyromaniac environment
pyro_env = Environment(
    variable_start_string="`", variable_end_string="`", finalize=json_finalize
)
pyro_env.filters['raw'] = lambda c: Raw(c)
pyro_env.filters['shell'] = shell
pyro_env.tests['ellipsis'] = ellipsis

# JSON environment
json_env = Environment(finalize=json_finalize)
json_env.filters['raw'] = lambda c: Raw(c)
json_env.filters['shell'] = shell
json_env.tests['ellipsis'] = ellipsis


# TOML environment
def toml(obj: Any) -> str:
    match obj:
        case dict():
            pairs = []
            for key, value in obj.items():
                if not isinstance(key, str):
                    raise ValueError(f"{repr(key)} is not a valid toml key")
                pairs.append(f"{toml(key)} = {toml(value)}")
            return "{ " + ", ".join(pairs) + " }"
        case list():
            return "[ " + ", ".join(toml(v) for v in obj) + " ]"
        case date() | datetime() | time():
            return obj.isoformat()
        case str() | int() | float() | bool():
            return json_dumps(obj)
        case Path() | URL():
            return toml(str(obj))
        case _:
            raise ValueError(f"{repr(obj)} is not toml serializable")


def toml_finalize(obj: Any) -> str:
    match obj:
        case Raw(content):
            return str(content)
        case _:
            return toml(obj)


toml_env = Environment(finalize=toml_finalize)
toml_env.filters['raw'] = lambda c: Raw(c)
toml_env.filters['shell'] = shell
toml_env.tests['ellipsis'] = ellipsis
