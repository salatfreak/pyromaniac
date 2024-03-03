from typing import Any
from unittest import TestCase
from pathlib import PosixPath as Path
import json
from pyromaniac.compiler.errors import NotADictError
from pyromaniac.compiler.compiler import Compiler


class TestCompiler(TestCase):
    def setUp(self):
        self.comps = Path(__file__).parent.joinpath("components")
        self.compiler = Compiler.create(self.comps)

    def test_minimal(self):
        self.assertEqual(list(self.compile("minimal").keys()), ["ignition"])

    def test_pyromaniac_object(self):
        address = ("http", "localhost", 8000)
        result = self.compile("pyromaniac_object", address, "secret")
        replace = result['ignition']['config']['replace']
        self.assertEqual(replace['source'], "http://localhost:8000/config.ign")
        self.assertEqual(replace['httpHeaders'][0]['value'], "Basic secret")

    def test_arguments(self):
        args = {"args": ["/foo"], "kwargs": {"content": "bar"}}
        file = self.compile("arguments", **args)['storage']['files'][0]
        self.assertEqual(file['path'], "/foo")
        self.assertIn("bar", json.dumps(file['contents']))

        args = {"args": ["/baz"]}
        file = self.compile("arguments", **args)['storage']['files'][0]
        self.assertEqual(file['path'], "/baz")
        self.assertIn("default", json.dumps(file['contents']))

    def test_not_a_dict_error(self):
        with self.assertRaises(NotADictError) as e:
            self.compile("returns_string")
        self.assertIsInstance(e.exception.result, str)

    def compile(
        self, path: str,
        address: tuple[str, str, int] = ("http", "localhost", 8000),
        auth: str | None = None,
        args: list = [], kwargs: dict[str, Any] = {},
    ) -> dict:
        source = self.comps.joinpath(path).with_suffix(".pyro").read_text()
        result = self.compiler.compile(source, address, auth, args, kwargs)
        return json.loads(result)
