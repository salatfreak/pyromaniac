from typing import Any
from json import JSONEncoder as JSONEncoderBase
from pathlib import PosixPath as Path

from ..url import URL


class JSONEncoder(JSONEncoderBase):
    """JSON encoder with support for Paths and URLs"""

    def default(self, o: Any) -> Any:
        match o:
            case Path() | URL():
                return str(o)
            case _:
                return super().default(o)
