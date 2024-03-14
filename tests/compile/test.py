from typing import Any
from unittest import TestCase
from unittest.mock import patch
import sys
from os import chdir
import json
from pathlib import PosixPath as Path
from pyromaniac import compile, Remote


@patch('pyromaniac.paths.stdlib', Path(__file__).parent.joinpath("stdlib"))
class TestCompile(TestCase):
    def setUp(self):
        dir = Path(__file__).parent.joinpath("components")
        sys.path.insert(0, str(dir))
        chdir(dir)

    def test_remote(self):
        remote = Remote.create(("http", "localhost", 8000), "secret")
        result = self.compile("remote", remote)
        replace = result["ignition"]["config"]["replace"]
        self.assertEqual(replace["source"], "http://localhost:8000/config.ign")
        self.assertEqual(replace["httpHeaders"][0]["value"], "Basic secret")

    def test_complex(self):
        result = self.compile("main", args=["/file"])
        self.assertEqual(len(result["ignition"]["config"]["merge"]), 2)

    def test_python_modules(self):
        result = self.compile("python")
        self.assertEqual(result['storage']['files'][0]['path'], "/69/42/42/69")

    def compile(
        self, path: str,
        remote: Remote = Remote.create(("http", "localhost", 8000)),
        args: list = [], kwargs: dict[str, Any] = {},
    ) -> Any:
        source = Path(path).with_suffix(".pyro").read_text()
        return json.loads(compile(source, remote, args, kwargs))
