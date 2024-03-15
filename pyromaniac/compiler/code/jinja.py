from typing import Any
from datetime import date, datetime, time
from pathlib import PosixPath as Path
from json import dumps as json_dumps, JSONEncoder as JSONEncoderBase
from jinja2 import Environment

from ..url import URL


# Raw object wrapper
class Raw:
    __match_args__ = ("content",)

    def __init__(self, content: Any):
        self.content = content


# JSON environments
class JSONEncoder(JSONEncoderBase):
    def default(self, obj: Any) -> Any:
        match obj:
            case Path() | URL(): return str(obj)
            case _: return super().default(obj)


def json_finalize(obj: Any) -> str:
    match obj:
        case Raw(content): return str(content)
        case _: return json_dumps(obj, cls=JSONEncoder)


pyro_env = Environment(
    variable_start_string="`", variable_end_string="`", finalize=json_finalize
)
pyro_env.filters['raw'] = lambda c: Raw(c)

json_env = Environment(finalize=json_finalize)
json_env.filters['raw'] = lambda c: Raw(c)


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
        case Raw(content): return str(content)
        case _: return toml(obj)


toml_env = Environment(finalize=toml_finalize)
toml_env.filters['raw'] = lambda c: Raw(c)
