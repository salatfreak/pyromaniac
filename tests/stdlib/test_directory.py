from pathlib import PosixPath as Path

from .base import TestCase


class TestDirectory(TestCase):
    comp = 'directory'

    def test_minimal(self):
        self.assertEqual(self.call("/foo"), {'path': Path("/foo")})

    def test_complex(self):
        self.assertEqual(
            self.call(
                "foo", "core", None, mode=0o550,
            ), {
                'path': Path("/home/core/foo"),
                'user': {'name': "core"},
                'mode': 0o550,
            }
        )
