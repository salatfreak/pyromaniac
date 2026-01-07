from pathlib import PosixPath as Path

from .base import TestCase

target = 'storage.directories[]'


class TestDirectory(TestCase):
    comp = 'std.directory'

    def test_minimal(self):
        self.assertEqual(self.call("/foo"), {
            'path': Path("/foo"), '__for__': target,
        })

    def test_complex(self):
        self.assertEqual(self.call("foo", "core", None, mode=0o550), {
            'path': Path("/home/core/foo"),
            'user': {'name': "core"},
            'mode': 0o550,
            '__for__': target,
        })
