from unittest import TestCase
from unittest.mock import patch, Mock
from collections.abc import Iterable
from pathlib import PosixPath as Path
from itertools import chain
from pyromaniac import paths
from pyromaniac.compiler import NotAComponentError
from pyromaniac.compiler.library import Library, View
from pyromaniac.compiler.component import Component


def glob(path: Path, *patterns: str) -> Iterable[str]:
    return chain(*(path.glob(p) for p in patterns))


@classmethod
def mock_create(cls: object, source: str) -> Component:
    return Component(None, None, None, None)


@patch('pyromaniac.compiler.component.Component.create', mock_create)
class TestLibrary(TestCase):
    def setUp(self):
        self.comps = Path(__file__).parent.joinpath("components")
        self.stdlib = Library(paths.stdlib)
        self.lib = Library(self.comps, [self.stdlib])

    def test_contains(self):
        for p in glob(self.comps, "**/*/", "**/*.pyro"):
            name = ".".join(p.relative_to(self.comps).with_suffix("").parts)
            self.assertIn(name, self.lib)
        for p in glob(self.comps, "**/*.json", "**/*.yml"):
            name = ".".join(p.relative_to(self.comps).with_suffix("").parts)
            self.assertNotIn(name, self.lib)
        for p in glob(paths.stdlib, "**/*/", "**/*.pyro"):
            name = ".".join(p.relative_to(paths.stdlib).with_suffix("").parts)
            self.assertIn(name, self.lib)
        self.assertNotIn("bananenbrot", self.lib)

    def test_dir(self):
        expected = set(
            p.stem
            for p in chain(*(p.glob("*") for p in [self.comps, paths.stdlib]))
        )
        self.assertEqual(self.lib.dir(), expected)

    def test_resolve(self):
        self.assertResolvesTo("comp1", "comp1")
        self.assertResolvesTo("dir1.dir11.comp111", "dir1.dir11.comp111")
        self.assertResolvesTo("dir1.dir11", "dir1.dir11.main")

        self.assertResolvesTo("merge", "merge", self.stdlib)

        self.assertResolvesTo("", None)
        self.assertResolvesTo(".", None)
        self.assertResolvesTo("comp11", None)
        self.assertResolvesTo("bananenbrot", None)

    @patch('pyromaniac.compiler.component.Component.execute')
    def test_execute(self, execute: Mock):
        execute.return_value = "foo"
        self.assertEqual(self.lib.execute("comp1", "foo", bar="baz"), "foo")
        self.assertEqual(execute.call_args.args[0].path, self.comps)
        self.assertEqual(execute.call_args.args[1:], ("foo",))
        self.assertEqual(execute.call_args.kwargs, {"bar": "baz"})

        execute.return_value = "pi"
        self.assertEqual(self.stdlib.execute("merge"), "pi")
        self.assertEqual(execute.call_args.args[0].path, paths.stdlib)

        with self.assertRaises(Exception):
            self.lib.execute("bananenbrot")

    def test_get(self):
        comp = self.lib.get('dir1.dir11.comp111')
        self.assertIsInstance(comp, Component)
        self.assertEqual(comp, self.lib.get('dir1.dir11.comp111'))
        self.assertNotEqual(comp, self.lib.get('dir1.dir11.main'))

    def assertResolvesTo(
        self, name: str, expected: str | None, lib: Library | None = None
    ):
        lib = lib or self.lib
        expected_tuple = (lib, expected) if expected is not None else None
        self.assertEqual(self.lib.resolve(name), expected_tuple)


@patch('pyromaniac.compiler.component.Component.create', mock_create)
class TestView(TestCase):
    def setUp(self):
        TestLibrary.setUp(self)
        self.view = self.lib.view()

    def test_getattr(self):
        self.assertIsInstance(self.view.dir1.dir11, View)
        self.assertIsInstance(self.view.dir1.dir11.comp111, View)
        self.assertIsInstance(self.view.merge, View)
        self.assertIsInstance(self.view.dir1._.dir1.dir11.main, View)
        self.assertIsInstance(self.view.dir1.dir11._._.merge, View)

        with self.assertRaises(AttributeError):
            self.view.bananenbrot
        with self.assertRaises(AttributeError):
            self.view.dir1.bananenbrot
        with self.assertRaises(AttributeError):
            self.view.dir1._.bananenbrot

    def test_contains(self):
        self.assertIn("dir1", self.view)
        self.assertIn("comp111", self.view.dir1._.dir1.dir11)
        self.assertIn("merge", self.view.dir1._)

        self.assertNotIn("bananenbrot", self.view.dir1)
        self.assertNotIn("merge", self.view.dir1)

    @patch('pyromaniac.compiler.component.Component.execute')
    def test_call(self, execute: Mock):
        execute.return_value = "foo"
        self.assertEqual(self.view.dir1.dir11.comp111("bar", baz="qux"), "foo")
        self.assertEqual(self.view.dir1.dir11("bar", baz="qux"), "foo")

        self.assertEqual(execute.call_args.args[1:], ("bar",))
        self.assertEqual(execute.call_args.kwargs, {"baz": "qux"})

        with self.assertRaises(NotAComponentError):
            self.view.dir1()
