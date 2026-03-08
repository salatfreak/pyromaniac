from pathlib import PosixPath as Path
from pyromaniac.compiler.url import URL

from .base import TestCase


class TestContents(TestCase):
    def test_minimal(self):
        path, url = Path("file.txt"), URL("https://example.com/")
        self.assertEqual(self.call('std.contents', "foo"), {"inline": "foo"})
        self.assertEqual(self.call('std.contents', path), {"local": path})
        self.assertEqual(self.call('std.contents', url), {"source": url})
        result = self.call('std.contents', {'inline': "foo"})
        self.assertEqual(result, {'inline': "foo"})

    def test_headers(self):
        path, url = Path("file.txt"), URL("https://example.com/")
        self.assertEqual(
            self.call('std.contents', "foo", headers={"bar": "baz"}),
            {"inline": "foo"},
        )
        self.assertEqual(
            self.call('std.contents', path, headers={"qux": "quux"}),
            {"local": path},
        )
        self.assertEqual(
            self.call('std.contents', url, headers={"corge": "waldo"}),
            {"source": url, "http_headers": [{"name": "corge", "value": "waldo"}]},
        )

        result = self.call('std.contents',
            {'inline': "foo", 'http_headers': [{'name': "bar", 'value': "baz"}]},
            headers={"qux": "quux"},
            http_headers=[{'name': "corge", 'value': "waldo"}],
        )
        self.assertEqual(set(result.keys()), {"inline", "http_headers"})
        self.assertEqual(sorted(result['http_headers'], key=lambda h: h['name']), [
            {'name': "bar", 'value': "baz"},
            {'name': "corge", 'value': "waldo"},
            {'name': "qux", 'value': "quux"}
        ])

    def test_complex(self):
        result = self.call('std.contents', {
            'source': "https://example.com/",
            'http_headers': [{'name': "foo", 'value': "bar"}],
        }, {
            "foo": "baz",
            "qux": "quux",
        }, http_headers=[
            {'name': "foo", 'value': "corge"},
            {'name': "fred", 'value': "waldo"},
        ], compression=None)

        self.assertEqual(
            set(result.keys()), set(['source', 'http_headers', 'compression'])
        )
        self.assertEqual(result['source'], "https://example.com/")
        self.assertEqual(result['compression'], None)
        headers = sorted(result['http_headers'], key=lambda d: d['name'])
        self.assertEqual(headers, [
            {'name': "foo", 'value': "bar"},
            {'name': "fred", 'value': "waldo"},
            {'name': "qux", 'value': "quux"},
        ])

    def test_parse(self):
        result = self.call('std.contents.parse', "foo")
        self.assertIsInstance(result, str)
        result = self.call('std.contents.parse', "./bar.txt")
        self.assertIsInstance(result, Path)
        result = self.call('std.contents.parse', "https://example.com/")
        self.assertIsInstance(result, URL)
