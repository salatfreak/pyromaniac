from pathlib import PosixPath as Path
from pyromaniac.compiler.url import URL

from .base import TestCase

target = 'storage.files[]'


class TestFile(TestCase):
    comp = 'std.file'

    def test_minimal(self):
        self.assertEqual(self.call("/foo.txt"), {
            'path': Path("/foo.txt"), '__for__': target,
        })

    def test_path(self):
        self.assertEqual(self.call("/foo.txt", Path("bar.txt")), {
            'path': Path("/foo.txt"),
            'contents': {
                'local': Path("bar.txt"),
            },
            '__for__': target,
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
                '__for__': target,
            },
        )

    def test_relative(self):
        self.assertEqual(self.call("foo.txt", "bar", "core"), {
            'path': Path("/home/core/foo.txt"),
            'contents': {'inline': "bar"},
            'user': {'name': "core"},
            'group': {'name': "core"},
            '__for__': target,
        })

    def test_append(self):
        self.assertEqual(self.call(
            "/foo.txt",
            append=["bar", Path("bar.txt"), URL("https://example.com/")],
            headers={"Authorization": "Basic secret"},
        ), {
            'path': Path("/foo.txt"),
            'append': [
                {'inline': "bar"},
                {'local': Path("bar.txt")},
                {
                    'source': URL("https://example.com/"),
                    'http_headers': [{
                        'name': "Authorization",
                        'value': "Basic secret",
                    }],
                },
            ],
            '__for__': target,
        })
