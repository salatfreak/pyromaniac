from pyromaniac.compiler.code.errors import PythonRuntimeError

from .base import TestCase

target = 'storage'


class TestStorage(TestCase):
    comp = 'std.storage'

    def test_minimal(self):
        self.assertEqual(self.call(), {'__for__': target})

    def test_multiple(self):
        file1 = {'__for__': 'storage.files[]', 'path': "/var/foo"}
        file2 = {'path': "/var/bar", 'user': {'name': "baz"}}
        dir = {'path': "/var/qux"}
        link = {'__for__': 'storage.links[]', 'path': "/var/quux", 'target': "/corge"}
        self.assertEqual(self.call(
            file1,
            {'__for__': 'storage', 'files': [file2], 'directories': [dir]},
            link,
        ), {
            '__for__': target,
            'files': [file1, file2],
            'directories': [dir],
            'links': [link],
        })

    def test_combine(self):
        file1 = {
            '__for__': 'storage.files[]',
            'path': "/var/foo", 'overwrite': True, 'mode': 0o600,
            'contents': {'inline': "foo"},
            'append': [{'inline': "bar"}],
        }
        file2 = {
            '__for__': 'storage.files[]',
            'path': "/var/foo", 'mode': 0o666,
            'contents': {'local': "baz"},
            'append': [{'local': "qux"}],
        }
        self.assertEqual(self.call(file1, file2), {'__for__': target, "files": [{
            '__for__': 'storage.files[]',
            'path': "/var/foo", 'overwrite': True, 'mode': 0o666,
            'contents': {'local': "baz"},
            'append': [{'inline': "bar"}, {'local': "qux"}],
        }]})

        tree1 = {'__for__': "storage.trees[]", 'local': "foo"}
        tree2 = {'__for__': "storage.trees[]", 'path': "/bar", 'local': "baz"}
        tree3 = {'__for__': "storage.trees[]", 'path': "/", 'local': "qux"}
        self.assertEqual(self.call(tree1, tree2, tree3), {'__for__': target, "trees": [
            {'__for__': "storage.trees[]", 'path': "/", 'local': "qux"},
            tree2
        ]})

    def test_wrong_for(self):
        with self.assertRaises(PythonRuntimeError) as e:
            self.call({})
        self.assertIsInstance(e.exception.__cause__, ValueError)

        with self.assertRaises(PythonRuntimeError) as e:
            self.call({'__for__': "foo"})
        self.assertIsInstance(e.exception.__cause__, ValueError)

    def test_invalid(self):
        with self.assertRaises(PythonRuntimeError) as e:
            self.call({'__for__': 'storage', 'files': [42]})
        self.assertIsInstance(e.exception.__cause__, ValueError)

        with self.assertRaises(PythonRuntimeError) as e:
            self.call({'__for__': 'storage.directories[]', 'not_path': "/var/foo"})
        self.assertIsInstance(e.exception.__cause__, ValueError)
