from typing import Any
from pathlib import PosixPath as Path
from json import dumps as json_dumps, JSONEncoder as JSONEncoderBase
from jinja2 import Environment

from ..url import URL


# Raw object wrapper
class Raw:
    __match_args__ = ("content",)

    def __init__(self, content: Any):
        self.content = content


# JSON environment
class JSONEncoder(JSONEncoderBase):
    def default(self, obj: Any) -> Any:
        match obj:
            case Path() | URL(): return str(obj)
            case _: return super().default(obj)


def json_finalize(obj: Any) -> str:
    match obj:
        case Raw(content): return str(content)
        case _: return json_dumps(obj, cls=JSONEncoder)


json_env = Environment(finalize=json_finalize)
json_env.filters['raw'] = lambda c: Raw(c)
