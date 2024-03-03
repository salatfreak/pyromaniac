from typing import Any, Self
from pathlib import PosixPath as Path

from .. import paths
from .pyromaniac import Pyromaniac
from .butane import butane
from .expand import expand
from .component import Component
from .library import Library
from .context import context


class Compiler:
    """Pyromaniac config compiler."""

    def __init__(self, lib: Library):
        self.lib = lib

    @classmethod
    def create(cls, path: Path) -> Self:
        """Create new config compiler.

        :param path: path to component library
        :returns: created compiler
        """
        return cls(Library(path, [Library(paths.stdlib)]))

    def compile(
        self, source: str,
        address: tuple[str, str, int], auth: str | None = None,
        args: list = [], kwargs: dict[str, Any] = {},
    ) -> str:
        """Compile config to ignition.

        :param source: pyromaniac config source text
        :param address: scheme, host and port for encryption secret requests
        :param auth: basic auth credentials for encryption secret requests
        :param args: positional arguments to pass to the component
        :param kwargs: keyword arguments to pass to the component
        :returns: compiled ignition config
        """
        vars = {'pyromaniac': Pyromaniac(address, auth)}
        ctx = context(self.lib, self.lib.view(), **vars)
        result = Component.create(source).execute(ctx, *args, **kwargs)
        return butane(expand(result, True, True))
