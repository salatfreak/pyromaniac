from unittest import TestCase
from unittest.mock import patch, Mock
from pathlib import PosixPath as Path
from pyromaniac import paths
from pyromaniac.compiler.context import Context, Underscore
from pyromaniac.compiler.library import Library, View


class TestContext(TestCase):
    def setUp(self):
        self.comps = Path(__file__).parent.joinpath("components")
        self.stdlib = Library(paths.stdlib)
        self.lib = Library(self.comps, [self.stdlib])
        self.root = Context(self.lib, self.lib.view(), self.comps)
        self.nested = Context(
            self.lib, self.lib.view("dir1.dir11"),
            self.comps.joinpath("dir1", "dir11"),
        )

    def test_dict(self):
        with self.assertRaises(KeyError):
            self.root["bananenbrot"]
        self.root["bananenbrot"] = "foo"
        self.assertEqual(self.root["bananenbrot"], "foo")

        self.assertIsInstance(self.nested['GLOBAL'], dict)
        self.nested['GLOBAL'] = "bar"
        self.assertEqual(self.nested['GLOBAL'], "bar")
        del self.nested['GLOBAL']
        self.assertIsInstance(self.nested['GLOBAL'], dict)

    def test_underscore(self):
        self.assertIsInstance(self.nested['_'], Underscore)

    def test_lib(self):
        self.assertIsInstance(self.root['dir1'].dir11, View)
        self.assertIsInstance(self.nested['merge'], View)

    def test_context(self):
        self.assertIsInstance(self.root['GLOBAL'], dict)
        self.root['GLOBAL']['foo'] = 'bar'
        self.assertEqual(self.root['GLOBAL']['foo'], 'bar')
        self.assertIs(self.root['GLOBAL'], self.nested['GLOBAL'])

    def test_keys(self):
        self.assertNotIn("bananenbrot", self.root.keys())
        self.root["bananenbrot"] = "foo"
        self.assertIn("bananenbrot", self.root.keys())
        self.assertNotIn("bananenbrot", self.nested.keys())

        self.assertIn('_', self.root.keys())
        self.assertIn('comp1', self.nested.keys())
        self.assertIn('merge', self.nested.keys())
        self.assertIn('expand', self.root.keys())

    def test_iter(self):
        self.assertTrue(any(k == '_' for k in self.root))
        self.assertTrue(any(k == 'comp1' for k in self.nested))


class TestUnderscore(TestCase):
    setUp = TestContext.setUp

    @patch('pyromaniac.compiler.component.Component.execute')
    def test_lib(self, execute: Mock):
        execute.return_value = {"foo": "bar"}
        self.assertIsInstance(self.root['_'].dir1.dir11.comp111, View)
        self.assertIsInstance(self.nested['_']._._.dir1.dir11(), dict)

    def test_path(self):
        self.assertTrue((self.root['_'] / "dir1/file11.json").exists())
        self.assertTrue((self.nested['_'] / "file111.yml").exists())
