from typing import Self
from pathlib import PosixPath as Path

from .. import paths
from .errors import NotADictError
from .pyromaniac import Pyromaniac
from .butane import butane
from .expand import expand
from .component import Component
from .library import Library
from .context import Context


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
    ) -> str:
        """Compile config to ignition.

        :param source: pyromaniac config source text
        :param address: scheme, host and port for encryption secret requests
        :param auth: basic auth credentials for encryption secret requests
        :returns: compiled ignition config
        """
        component = Component.create(source)

        context = Context(self.lib, self.lib.view(), self.lib.get_path(""))
        context["pyromaniac"] = Pyromaniac(address, auth)

        result = component.execute(context)
        if not isinstance(result, dict):
            raise NotADictError(result)

        return butane(expand(result, True, True))
