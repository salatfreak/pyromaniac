from typing import Self
from pathlib import PosixPath as Path
import json

from .butane import butane
from .expand import expand


class Compiler:
    """Pyromaniac config compiler."""

    @classmethod
    def create(cls, path: Path) -> Self:
        """Create new config compiler.

        :param path: path to component library
        :returns: created compiler
        """
        return cls()

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
        return butane(expand(json.loads(source), True, True))
