from unittest import TestCase
from unittest.mock import patch, Mock
from pathlib import PosixPath as Path
from pyromaniac import paths
from pyromaniac.compiler.context import Context, Underscore
from pyromaniac.compiler.library import Library, View


class TestContext(TestCase):
    def setUp(self):
        self.comps = Path(__file__).parent.parent.joinpath("components")
        self.stdlib = Library(paths.stdlib)
        self.lib = Library(self.comps, [self.stdlib])
        self.root = Context(self.lib, self.lib.view(), self.comps)
        self.baz = Context(
            self.lib, self.lib.view("foo.baz"),
            self.comps.joinpath("foo", "baz"),
        )

    def test_dict(self):
        with self.assertRaises(KeyError):
            self.root["bananenbrot"]
        self.root["bananenbrot"] = "foo"
        self.assertEqual(self.root["bananenbrot"], "foo")

        self.assertIsInstance(self.baz['GLOBAL'], dict)
        self.baz['GLOBAL'] = "bar"
        self.assertEqual(self.baz['GLOBAL'], "bar")
        del self.baz['GLOBAL']
        self.assertIsInstance(self.baz['GLOBAL'], dict)

    def test_underscore(self):
        self.assertIsInstance(self.baz['_'], Underscore)

    def test_lib(self):
        self.assertIsInstance(self.root['foo'].baz, View)
        self.assertIsInstance(self.baz['merge'], View)

    def test_context(self):
        self.assertIsInstance(self.root['GLOBAL'], dict)
        self.root['GLOBAL']['foo'] = 'bar'
        self.assertEqual(self.root['GLOBAL']['foo'], 'bar')
        self.assertIs(self.root['GLOBAL'], self.baz['GLOBAL'])

    def test_keys(self):
        self.assertNotIn("bananenbrot", self.root.keys())
        self.root["bananenbrot"] = "foo"
        self.assertIn("bananenbrot", self.root.keys())
        self.assertNotIn("bananenbrot", self.baz.keys())

        self.assertIn('_', self.root.keys())
        self.assertIn('foo', self.baz.keys())
        self.assertIn('merge', self.baz.keys())
        self.assertIn('expand', self.root.keys())

    def test_iter(self):
        self.assertTrue(any(k == '_' for k in self.root))
        self.assertTrue(any(k == 'foo' for k in self.baz))


class TestUnderscore(TestCase):
    setUp = TestContext.setUp

    @patch('pyromaniac.compiler.component.Component.execute')
    def test_lib(self, execute: Mock):
        execute.return_value = {"foo": "bar"}
        self.assertIsInstance(self.root['_'].foo.baz, View)
        self.assertIsInstance(self.baz['_']._._.foo.corge("baz"), dict)

    def test_path(self):
        self.assertIsInstance(self.root['_'] / "foo/data.json", Path)
        self.assertTrue((self.root['_'] / "foo/data.json").exists())
        self.assertTrue((self.baz['_'] / "data.yml").exists())
