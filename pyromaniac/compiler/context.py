from typing import Any, TYPE_CHECKING
from pathlib import PosixPath as Path

from .url import URL
from .expand import expand
from .butane import butane

if TYPE_CHECKING:
    from .library import Library, View

CONTEXT = {
    'Any': Any, 'Path': Path, 'URL': URL,
    'butane': butane, 'expand': expand,
    'GLOBAL': {}
}


def context(lib: 'Library', view: 'View', **kwargs) -> dict:
    return {**CONTEXT, **lib, **{"_": view}, **kwargs}
