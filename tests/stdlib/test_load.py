from pyromaniac.compiler.code.errors import PythonRuntimeError

from .base import TestCase


class TestLoad(TestCase):
    def test_text(self):
        file = self.lib.view() / "greeting.txt"

        result = self.call('std.load', file)
        self.assertEqual(result, file.read_text())

        result = self.call('std.load', file, name="Alice")
        self.assertEqual(result.strip(), "Hello, Alice!")

        result = self.call('std.load', file, foo="bar")
        self.assertEqual(result.strip(), "Hello, Bob!")

    def test_json(self):
        self.structured("json")

    def test_yaml(self):
        self.structured("yaml")

    def test_toml(self):
        self.structured("toml")

    def structured(self, type: str):
        comp = f'std.load.{type}'
        file = self.lib.view() / f"file.{type}"

        with self.assertRaises(PythonRuntimeError):
            self.call(comp, file)

        result = self.call(comp, file, name="Muhammad")
        self.assertEqual(result["name"], "Muhammad Li")
        self.assertEqual(result["hobbies"], ["programming"])

        hobby = ["eating", {"today": "potatoes"}]
        result = self.call(comp, file, name="Alice", hobby=hobby)
        self.assertEqual(result["name"], "Alice Li")
        self.assertEqual(result["hobbies"][0][1]["today"], "potatoes")
