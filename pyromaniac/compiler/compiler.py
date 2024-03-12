from typing import Any, Self, TYPE_CHECKING
from pathlib import PosixPath as Path

from .. import paths
from .butane import butane
from .expand import expand
from .component import Component
from .library import Library
from .context import context

if TYPE_CHECKING:
    from ..remote import Remote


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
        self, source: str, remote: 'Remote',
        args: tuple = tuple(), kwargs: dict[str, Any] = {},
    ) -> str:
        """Compile config to ignition.

        :param source: pyromaniac config source text
        :param remote: remote object with address and authentication secret
        :param args: positional arguments to pass to the component
        :param kwargs: keyword arguments to pass to the component
        :returns: compiled ignition config
        """
        ctx = context(self.lib, self.lib.view(), remote=remote)
        result = Component.create(source).execute(ctx, args, kwargs)
        return butane(expand(result, True, True))
