from typing import Any
from collections.abc import Iterable, Mapping
from datetime import date, datetime, time
from pathlib import PosixPath as Path
import re
from json import dumps as json_dumps
from jinja2 import Environment

from ..url import URL
from .json import JSONEncoder
from .runext import RunExtension

SAFE_SHELL_ARG_RE = re.compile(r'^[\w./:+,@=-]+$')


# extra filters
class Raw:
    __match_args__ = ("content",)

    def __init__(self, content: Any):
        self.content = content


def filter_shell(content: Any) -> str:
    if isinstance(content, str | bytes) or not isinstance(content, Iterable):
        content = [content]
    return " ".join(escape_shell_arg(str(arg)) for arg in content)


def escape_shell_arg(arg: str):
    if SAFE_SHELL_ARG_RE.fullmatch(arg):
        return arg
    return "'" + arg.replace("'", r"'\''") + "'"


filters = {"raw": Raw, "shell": filter_shell}


# extra tests
def test_series(val: Any) -> bool:
    return isinstance(val, Iterable) and not isinstance(val, str | bytes | Mapping)


def test_ellipsis(val: Any) -> bool:
    return val is Ellipsis


tests = {"series": test_series, "ellipsis": test_ellipsis}


# default environment
default_env = Environment()
default_env.filters.update({k: v for k, v in filters.items() if k != 'raw'})
default_env.tests.update(tests)


# JSON environment
def json_finalize(obj: Any) -> str:
    match obj:
        case Raw(content):
            return str(content)
        case _:
            return json_dumps(obj, cls=JSONEncoder)


json_env = Environment(finalize=json_finalize)
json_env.filters.update(filters)
json_env.tests.update(tests)


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
toml_env.filters.update(filters)
toml_env.tests.update(tests)


# pyromaniac environment
pyro_env = Environment(
    variable_start_string="`", variable_end_string="`", finalize=json_finalize,
    extensions=[RunExtension],
)
pyro_env.filters.update(filters)
pyro_env.tests.update(tests)
