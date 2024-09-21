from pathlib import PosixPath as Path
from json import loads
from pyromaniac.compiler.url import URL

from .base import TestCase


class TestMerge(TestCase):
    comp = 'std.merge'

    def test_types(self):
        result = self.call("{}", Path("/foo.txt"), URL("https://bar.com/"))
        self.assertEqual(result, [
            {'inline': "{}"},
            {'local': Path("/foo.txt")},
            {'source': URL("https://bar.com/")},
        ])

    def test_render(self):
        result = self.call("{}", {'storage.files[0].path': "/foo.txt"})
        self.assertEqual(result[0], {'inline': "{}"})
        self.assertEqual(loads(result[1]['inline'])['storage'], {
            'files': [{'path': "/foo.txt"}],
        })

    def test_headers(self):
        headers = {"Authorization": "Basic secret"}
        result = self.call("{}", URL("https://bar.com/"), headers=headers)
        self.assertEqual(result, [{
            'inline': "{}",
        }, {
            'source': URL("https://bar.com/"),
            'http_headers': [
                {'name': "Authorization", 'value': "Basic secret"},
            ],
        }])
