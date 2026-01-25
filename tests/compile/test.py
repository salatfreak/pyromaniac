from typing import Any
from unittest import TestCase
from unittest.mock import patch
import sys
from os import chdir
import json
from pathlib import PosixPath as Path
from pyromaniac import compile, Remote
from pyromaniac.compiler.code.errors import YamlExecutionError


@patch('pyromaniac.paths.stdlib', Path(__file__).parent.joinpath("stdlib"))
class TestCompile(TestCase):
    def setUp(self):
        dir = Path(__file__).parent.joinpath("components")
        sys.path.insert(0, str(dir))
        chdir(dir)

    def test_args(self):
        result = self.compile(
            "args", args=("zeus", "--debug", "--", "mod1", "--mod2"), parse_args=True,
        )
        file = result['storage']['files'][0]
        self.assertEqual(file['path'], "/etc/zeus.conf")
        self.assertIn("--MOD2", file['contents']['source'])

    def test_remote(self):
        remote = Remote.create(("http", "localhost", 8000), "secret")
        result = self.compile("remote", remote)
        replace = result["ignition"]["config"]["replace"]
        self.assertEqual(replace["source"], "http://localhost:8000/config.ign")
        self.assertEqual(replace["httpHeaders"][0]["value"], "Basic secret")

    def test_path(self):
        with self.assertRaises(YamlExecutionError):
            self.compile("nested/some_more/main.pyro")
        result = self.compile("nested/some_more/main.pyro", path="nested.some_more")
        contents = result['storage']['files'][0]['contents']
        self.assertEqual(contents['source'], "data:,bar")

    def test_complex(self):
        result = self.compile("main", args=("/file",))
        self.assertEqual(len(result['ignition']['config']['merge']), 2)

    def test_python_modules(self):
        result = self.compile("python")
        self.assertEqual(result['storage']['files'][0]['path'], "/69/42/42/69")

    def compile(
        self, comp: str,
        remote: Remote = Remote.create(("http", "localhost", 8000)), path: str = "",
        args: tuple = (), kwargs: dict[str, Any] = {}, parse_args: bool = False,
    ) -> Any:
        source = Path(comp).with_suffix(".pyro").read_text()
        return json.loads(compile(source, remote, path, args, kwargs, parse_args))
