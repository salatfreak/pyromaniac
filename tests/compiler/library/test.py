from unittest import TestCase
from unittest.mock import patch, Mock
from collections.abc import Iterable
from pathlib import PosixPath as Path
from itertools import chain
from pyromaniac.compiler.errors import NonExistentPathError, NotAComponentError
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
        self.std = Path(__file__).parent.joinpath("stdlib")
        self.stdlib = Library(self.std)
        self.lib = Library(self.comps, [self.stdlib])

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
        self.assertEqual(execute.call_args.args[1:], ("foo",))
        self.assertEqual(execute.call_args.kwargs, {"bar": "baz"})

        execute.return_value = "pi"
        self.assertEqual(self.stdlib.execute("merge"), "pi")

    def test_get_component(self):
        comp = self.lib.get_component('dir1.dir11.comp111')
        self.assertIsInstance(comp, Component)
        self.assertIs(comp, self.lib.get_component('dir1.dir11.comp111'))
        self.assertNotEqual(comp, self.lib.get_component('dir1.dir11.main'))

    def test_getitem(self):
        self.assertIsInstance(self.lib[""], View)
        self.assertIsInstance(self.lib["dir1.dir11.comp111"], View)
        self.assertIsInstance(self.lib["merge"], View)
        self.assertIsInstance(self.lib["dir1.dir11"], View)

        with self.assertRaises(KeyError):
            self.lib["0comp"]

    def test_contains(self):
        for p in glob(self.comps, "**/*/", "**/*.pyro"):
            name = ".".join(p.relative_to(self.comps).with_suffix("").parts)
            if not name.split(".")[-1].startswith("0"):
                self.assertIn(name, self.lib)
        for p in glob(self.comps, "**/*.json", "**/*.yml"):
            name = ".".join(p.relative_to(self.comps).with_suffix("").parts)
            self.assertNotIn(name, self.lib)
        for p in glob(self.std, "**/*/", "**/*.pyro"):
            name = ".".join(p.relative_to(self.std).with_suffix("").parts)
            self.assertIn(name, self.lib)
        self.assertNotIn("0comp", self.lib)
        self.assertNotIn("bananenbrot", self.lib)

    def test_keys(self):
        expected = set(
            p.stem
            for p in chain(*(p.glob("*") for p in [self.comps, self.std]))
            if not p.name.startswith("0")
        )
        self.assertEqual(set(self.lib.keys()), expected)

    def test_unpack(self):
        self.assertEqual(set({**self.lib}.keys()), {"comp1", "dir1", "merge"})

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

        with self.assertRaises(NonExistentPathError):
            self.view.bananenbrot._._
        with self.assertRaises(NonExistentPathError):
            self.view.bananenbrot
        with self.assertRaises(NonExistentPathError):
            self.view.dir1.bananenbrot
        with self.assertRaises(NonExistentPathError):
            self.view.dir1._.bananenbrot

    @patch('pyromaniac.compiler.component.Component.execute')
    def test_call(self, execute: Mock):
        execute.return_value = "foo"
        self.assertEqual(self.view.dir1.dir11.comp111("bar", baz="qux"), "foo")
        self.assertEqual(self.view.dir1.dir11("bar", baz="qux"), "foo")

        self.assertEqual(execute.call_args.args[1:], ("bar",))
        self.assertEqual(execute.call_args.kwargs, {"baz": "qux"})

        with self.assertRaises(NotAComponentError):
            self.view.dir1()

    def test_truediv(self):
        self.assertEqual(self.view / "", self.comps)
        self.assertEqual(
            self.view.dir1.dir11._ / "foo.txt",
            self.comps.joinpath("dir1/foo.txt"),
        )
