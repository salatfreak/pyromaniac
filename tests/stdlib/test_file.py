from pathlib import PosixPath as Path
from pyromaniac.compiler.url import URL

from .base import TestCase


class TestFile(TestCase):
    comp = 'file'

    def test_minimal(self):
        self.assertEqual(self.call("/foo.txt"), {'path': Path("/foo.txt")})

    def test_path(self):
        self.assertEqual(self.call("/foo.txt", Path("bar.txt")), {
            'path': Path("/foo.txt"),
            'contents': {
                'local': Path("bar.txt"),
            },
        })

    def test_url(self):
        self.assertEqual(
            self.call(
                "/foo.txt", URL("https://example.com/"),
                headers={"Authorization": "Basic secret"},
            ), {
                'path': Path("/foo.txt"),
                'contents': {
                    'source': URL("https://example.com/"),
                    'http_headers': [{
                        'name': "Authorization",
                        'value': "Basic secret",
                    }],
                },
            },
        )

    def test_relative(self):
        self.assertEqual(self.call("foo.txt", "bar", "core"), {
            'path': Path("/home/core/foo.txt"),
            'contents': {'inline': "bar"},
            'user': {'name': "core"},
            'group': {'name': "core"},
        })
