from typing import Any
from unittest import TestCase
from unittest.mock import patch
from os import chdir
import json
from pathlib import PosixPath as Path
from pyromaniac import compile


@patch('pyromaniac.paths.stdlib', Path(__file__).parent.joinpath("stdlib"))
class TestCompile(TestCase):
    def setUp(self):
        chdir(Path(__file__).parent.joinpath("components"))

    def test_remote(self):
        result = self.compile("remote", auth="secret")
        replace = result["ignition"]["config"]["replace"]
        self.assertEqual(replace["source"], "http://localhost:8000/config.ign")
        self.assertEqual(replace["httpHeaders"][0]["value"], "Basic secret")

    def test_complex(self):
        result = self.compile("main", args=["/file"])
        self.assertEqual(len(result["ignition"]["config"]["merge"]), 2)

    def compile(
        self, path: str,
        address: tuple[str, str, int] = ("http", "localhost", 8000),
        auth: str | None = None,
        args: list = [], kwargs: dict[str, Any] = {},
    ) -> Any:
        source = Path(path).with_suffix(".pyro").read_text()
        return json.loads(compile(source, address, auth, args, kwargs))
