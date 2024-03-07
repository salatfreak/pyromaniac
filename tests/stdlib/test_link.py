from pathlib import PosixPath as Path

from .base import TestCase


class TestLink(TestCase):
    comp = 'link'

    def test_minimal(self):
        self.assertEqual(self.call("/foo.txt", "/bar.txt"), {
            'path': Path("/foo.txt"),
            'target': Path("/bar.txt"),
        })

    def test_complex(self):
        self.assertEqual(
            self.call(
                "foo.txt", "bar.txt", "core", None, hard=True
            ), {
                'path': Path("/home/core/foo.txt"),
                'target': Path("bar.txt"),
                'user': {'name': "core"},
                'hard': True,
            }
        )
