from pathlib import PosixPath as Path

from .base import TestCase

target = 'storage.links[]'


class TestLink(TestCase):
    comp = 'std.link'

    def test_minimal(self):
        self.assertEqual(self.call("/foo.txt", "/bar.txt"), {
            'path': Path("/foo.txt"),
            'target': Path("/bar.txt"),
            '__for__': target,
        })

    def test_complex(self):
        self.assertEqual(
            self.call(
                "foo.txt", "bar.txt", "core", None, hard=True,
            ), {
                'path': Path("/home/core/foo.txt"),
                'target': Path("bar.txt"),
                'user': {'name': "core"},
                'hard': True,
                '__for__': target,
            }
        )
