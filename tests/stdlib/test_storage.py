from pyromaniac.compiler.code.errors import PythonRuntimeError

from .base import TestCase

target = 'storage'


class TestStorage(TestCase):
    comp = 'std.storage'

    def test_minimal(self):
        self.assertEqual(self.call(), {'__for__': target})

    def test_multiple(self):
        file = {'__for__': 'storage.files[]', 'foo': "bar"}
        link = {'__for__': 'storage.links[]', 'baz': 1337}
        self.assertEqual(self.call(
            file,
            {'__for__': 'storage', 'files': [42], 'directories': [69]},
            link,
        ), {
            '__for__': target,
            'files': [file, 42],
            'directories': [69],
            'links': [link],
        })

    def test_wrong_for(self):
        with self.assertRaises(PythonRuntimeError) as e:
            self.call({})
        self.assertIsInstance(e.exception.__cause__, ValueError)

        with self.assertRaises(PythonRuntimeError) as e:
            self.call({'__for__': "foo"})
        self.assertIsInstance(e.exception.__cause__, ValueError)

    def test_mismatch(self):
        with self.assertRaises(PythonRuntimeError) as e:
            self.call(
                {'__for__': 'storage', 'foo': {}},
                {'__for__': 'storage', 'foo': 42}
            )
        self.assertIsInstance(e.exception.__cause__, TypeError)

        with self.assertRaises(PythonRuntimeError) as e:
            self.call(
                {'__for__': 'storage.foo.bar[]', 'baz': 69},
                {'__for__': 'storage.foo.bar', 'baz': -1},
            )
        self.assertIsInstance(e.exception.__cause__, TypeError)
