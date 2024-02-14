from unittest import TestCase
from unittest.mock import patch, Mock
from collections.abc import Iterable
from pathlib import PosixPath as Path
from itertools import chain
from pyromaniac import paths
from pyromaniac.compiler.errors import NotAComponentError
from pyromaniac.compiler.library import Library, View
from pyromaniac.compiler.component import Component


def glob(path: Path, *patterns: str) -> Iterable[str]:
    return chain(*(path.glob(p) for p in patterns))


class TestLibrary(TestCase):
    def setUp(self):
        self.comps = Path(__file__).parent.parent.joinpath("components")
        self.stdlib = Library(paths.stdlib)
        self.lib = Library(self.comps, [self.stdlib])

    def test_contains(self):
        for p in glob(self.comps, "**/*/", "**/*.pyro"):
            name = ".".join(p.relative_to(self.comps).with_suffix("").parts)
            self.assertIn(name, self.lib)
        for p in glob(self.comps, "**/*.json", "**/*.yml", "**/*.toml"):
            name = ".".join(p.relative_to(self.comps).with_suffix("").parts)
            self.assertNotIn(name, self.lib)
        for p in glob(paths.stdlib, "**/*/", "**/*.pyro"):
            name = ".".join(p.relative_to(paths.stdlib).with_suffix("").parts)
            self.assertIn(name, self.lib)
        self.assertNotIn("baz", self.lib)

    def test_dir(self):
        expected = set(
            p.stem
            for p in chain(*(p.glob("*") for p in [self.comps, paths.stdlib]))
        )
        self.assertEqual(self.lib.dir(), expected)

    def test_resolve(self):
        self.assertResolvesTo("qux", "qux")
        self.assertResolvesTo("foo.baz.grault", "foo.baz.grault")
        self.assertResolvesTo("foo.baz", "foo.baz")
        self.assertResolvesTo("bar", "bar.main")

        self.assertResolvesTo("merge", "merge", self.stdlib)

        self.assertResolvesTo("", None)
        self.assertResolvesTo(".", None)
        self.assertResolvesTo("foo", None)
        self.assertResolvesTo("bananenbrot", None)

    @patch('pyromaniac.compiler.component.Component.execute')
    def test_execute(self, execute: Mock):
        execute.return_value = "foo"
        self.assertEqual(self.lib.execute("qux", "quux", corge="fred"), "foo")
        self.assertEqual(execute.call_args.args[0].path, self.comps)
        self.assertEqual(execute.call_args.args[1:], ("quux",))
        self.assertEqual(execute.call_args.kwargs, {"corge": "fred"})

        execute.return_value = "pi"
        self.assertEqual(self.stdlib.execute("merge"), "pi")
        self.assertEqual(execute.call_args.args[0].path, paths.stdlib)

        with self.assertRaises(Exception):
            self.lib.execute("bananenbrot")

    def test_get(self):
        comp = self.lib.get('foo.baz.grault')
        self.assertIsInstance(comp, Component)
        self.assertEqual(comp, self.lib.get('foo.baz.grault'))
        self.assertNotEqual(comp, self.lib.get('bar.main'))

    def assertResolvesTo(
        self, name: str, expected: str | None, lib: Library | None = None
    ):
        lib = lib or self.lib
        expected_tuple = (lib, expected) if expected is not None else None
        self.assertEqual(self.lib.resolve(name), expected_tuple)


class TestView(TestCase):
    def setUp(self):
        TestLibrary.setUp(self)
        self.view = self.lib.view()

    def test_getattr(self):
        self.assertIsInstance(self.view.foo.baz, View)
        self.assertIsInstance(self.view.foo.baz.waldo, View)
        self.assertIsInstance(self.view.merge, View)
        self.assertIsInstance(self.view.foo.baz._._.bar.main, View)
        self.assertIsInstance(self.view.foo.baz._._.merge, View)

        with self.assertRaises(AttributeError):
            self.view.bananenbrot
        with self.assertRaises(AttributeError):
            self.view.foo.bananenbrot
        with self.assertRaises(AttributeError):
            self.view.foo._.bananenbrot

    def test_contains(self):
        self.assertIn("foo", self.view)
        self.assertIn("baz", self.view.bar._.foo)
        self.assertIn("merge", self.view.foo._)

        self.assertNotIn("bar", self.view.foo)
        self.assertNotIn("merge", self.view.foo)

    @patch('pyromaniac.compiler.component.Component.execute')
    def test_call(self, execute: Mock):
        execute.return_value = "qux"
        self.assertEqual(self.view.foo.baz.grault("foo", bar="baz"), "qux")
        self.assertEqual(self.view.bar("foo", bar="baz"), "qux")
        self.assertEqual(self.view.foo.baz("foo", bar="baz"), "qux")

        self.assertEqual(execute.call_args.args[1:], ("foo",))
        self.assertEqual(execute.call_args.kwargs, {"bar": "baz"})

        with self.assertRaises(NotAComponentError):
            self.view.foo()
