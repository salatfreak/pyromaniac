from pathlib import PosixPath as Path

from .base import TestCase

target = 'storage.trees[]'


class TestTree(TestCase):
    comp = 'std.tree'

    def test_minimal(self):
        self.assertEqual(self.call("/foo", "bar"), {
            'path': Path("/foo"), 'local': Path("bar"), '__for__': target,
        })

    def test_complex(self):
        self.assertEqual(self.call("foo", "bar", "core", None, dir_mode=0o555), {
            'path': Path("/home/core/foo"),
            'local': Path("bar"),
            'user': {'name': "core"},
            'dir_mode': 0o555,
            '__for__': target,
        })
