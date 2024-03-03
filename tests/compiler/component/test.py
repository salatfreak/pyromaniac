from unittest import TestCase
from pathlib import PosixPath as Path
from pyromaniac.compiler.code.errors import InvalidArgumentError
from pyromaniac.compiler.context import context
from pyromaniac.compiler.component import Component
from pyromaniac.compiler.library import Library


class TestComponent(TestCase):
    def setUp(self):
        self.comps = Path(__file__).parent.joinpath("components")
        stdlib = Path(__file__).parent.joinpath("stdlib")
        lib = Library(self.comps, [Library(stdlib)])
        self.ctx = context(lib, lib.view())

    def test_minimal(self):
        comp = self.load("minimal")
        self.assertIsNone(comp.doc)
        self.assertIsNone(comp.python)
        self.assertIsNotNone(comp.yaml)
        self.assertEqual(comp.execute(self.ctx), {})

    def test_pure_yaml(self):
        comp = self.load("pure_yaml")
        result = comp.execute(self.ctx, ("qux",), {"foo": "quux"})
        self.assertEqual(result, [{"bar": "qux", "baz": "quux"}])

    def test_pure_python(self):
        comp = self.load("pure_python")
        self.assertIsNone(comp.doc)
        self.assertIsNotNone(comp.python)
        self.assertIsNone(comp.yaml)
        result = comp.execute(self.ctx, ("qux",), {"foo": "quux"})
        self.assertEqual(result, [{"bar": "qux", "baz": "quux"}])

    def test_yaml_with_sig(self):
        comp = self.load("yaml_with_sig")
        result = comp.execute(self.ctx, ("fred", 42))
        self.assertEqual(result, [{"bar": "fred", "baz": 42, "qux": "quux"}])
        result = comp.execute(self.ctx, ("fred",), {"baz": 69, "qux": "waldo"})
        self.assertEqual(result, [{"bar": "fred", "baz": 69, "qux": "waldo"}])

    def test_python_with_sig(self):
        comp = self.load("python_with_sig")
        self.assertEqual(comp.execute(self.ctx, (42,)), 42 * 2)

    def test_all(self):
        comp = self.load("all")
        self.assertIsNotNone(comp.doc)
        self.assertIsNotNone(comp.sig)
        self.assertIsNotNone(comp.python)
        self.assertIsNotNone(comp.yaml)
        args = ("Alice", 42, "programmer", "handstand", "trains")
        self.assertEqual(comp.execute(self.ctx, args), {
            "name": "Alice X", "age": 42, "job": "programmer",
            "intro": "I like handstand. I like trains.",
        })
        self.assertEqual(comp.execute(self.ctx, ("Bob", 69)), {
            "name": "Bob X", "age": 69, "job": "making worlds", "intro": "",
        })

    def test_invalid_argument(self):
        comp = self.load("yaml_with_sig")
        with self.assertRaises(InvalidArgumentError):
            comp.execute(self.ctx)
        with self.assertRaises(InvalidArgumentError):
            comp.execute(self.ctx, ("foo", "bar",))
        with self.assertRaises(InvalidArgumentError):
            comp.execute(self.ctx, ("foo", 42, None))

    def load(self, path: str, *args, **kwargs) -> Component:
        source = self.comps.joinpath(path).with_suffix(".pyro").read_text()
        return Component.create(source)
