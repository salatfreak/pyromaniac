from typing import Any, TYPE_CHECKING
from collections.abc import Iterable
from pathlib import PosixPath as Path

from .expand import expand
from .butane import butane

if TYPE_CHECKING:
    from .library import Library, View

CONTEXT = {'butane': butane, 'expand': expand, 'GLOBAL': {}}


class Context(dict):
    def __init__(self, lib: 'Library', view: 'View', path: Path):
        super().__init__()
        self.lib = lib
        self.view = view
        self.path = path

    def __getitem__(self, key: str) -> Any:
        """Retrieve arbitrary value, Underscore, Library, or helper.

        :param key: key to retrieve value for
        :returns: value associated with key
        """
        if super().__contains__(key):
            return super().__getitem__(key)
        if key == '_':
            return Underscore(self.view, self.path)
        if self.lib.__contains__(f".{key}"):
            return self.lib.view(f".{key}")
        return CONTEXT.__getitem__(key)

    # methods for dict expansion by jinja
    def keys(self) -> set[str]:
        return set(super().keys()) \
            .union(['_']) \
            .union(self.lib.dir()) \
            .union(CONTEXT.keys())

    def __iter__(self) -> Iterable[str]:
        return self.keys().__iter__()


class Underscore:
    def __init__(self, view: 'View', path: Path):
        self.__view = view
        self.__path = path

    def __getattr__(self, name: str) -> Any:
        return self.__view.__getattr__(name)

    def __truediv__(self, other: Path | str) -> Path:
        return self.__path.joinpath(other)
