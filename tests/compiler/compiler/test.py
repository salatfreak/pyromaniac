from unittest import TestCase
from pathlib import PosixPath as Path
import json
from pyromaniac.compiler import NotADictError
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
        merge = result['ignition']['config']['merge'][0]
        self.assertEqual(merge['source'], "http://localhost:8000/config.ign")
        self.assertEqual(merge['httpHeaders'][0]['value'], "Basic secret")

    def test_not_a_dict_error(self):
        with self.assertRaises(NotADictError) as e:
            self.compile("returns_string")
        self.assertIsInstance(e.exception.result, str)

    def compile(
        self, path: str,
        address: tuple[str, str, int] = ("http", "localhost", 8000),
        auth: str | None = None
    ) -> dict:
        source = self.comps.joinpath(path).with_suffix(".pyro").read_text()
        return json.loads(self.compiler.compile(source, address, auth))
