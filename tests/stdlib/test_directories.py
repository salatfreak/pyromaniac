from pathlib import PosixPath as Path
from pyromaniac.compiler.code.errors import PythonRuntimeError

from .base import TestCase


class TestDirectories(TestCase):
    comp = 'directories'

    def test_minimal(self):
        self.assertEqual(self.call("/foo", "bar"), [{
            'path': Path("/foo/bar"),
        }])

    def test_complex(self):
        self.assertEqual(
            self.call(
                ".config", "systemd/user", "core", None, overwrite=True,
            ), [{
                'path': Path("/home/core/.config/systemd"),
                'user': {'name': "core"},
                'overwrite': True,
            }, {
                'path': Path("/home/core/.config/systemd/user"),
                'user': {'name': "core"},
                'overwrite': True,
            }]
        )

    def test_not_relative(self):
        with self.assertRaises(PythonRuntimeError):
            self.call("/foo", "/bar/baz")
