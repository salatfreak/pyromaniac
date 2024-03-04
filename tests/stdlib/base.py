from typing import Any
from unittest import TestCase
from pathlib import PosixPath as Path
from pyromaniac import paths
from pyromaniac.compiler.library import Library


class TestCase(TestCase):
    def setUp(self):
        comps = Path(__file__).parent.joinpath("components")
        self.lib = Library(comps, [Library(paths.stdlib)])

    def execute(
        self, name: str, args: tuple = tuple(), kwargs: dict[str, Any] = {},
    ) -> Any:
        lib, path = self.lib.resolve(name)
        return lib.execute(path, args, kwargs)

    def call(self, *args: Any, **kwargs: Any) -> Any:
        match hasattr(self, 'comp'):
            case True: comp = self.comp
            case False: comp, args = args[0], args[1:]
        return self.execute(comp, args, kwargs)
