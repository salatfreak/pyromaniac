from pathlib import PosixPath as Path
from json import loads
from pyromaniac.compiler.url import URL

from .base import TestCase

target = 'ignition.config.merge[]'


class TestMerge(TestCase):
    comp = 'std.merge'

    def test_types(self):
        result = self.call("{}", Path("/foo.txt"), URL("https://bar.com/"))
        self.assertEqual(result, [
            {'inline': "{}", '__for__': target},
            {'local': Path("/foo.txt"), '__for__': target},
            {'source': URL("https://bar.com/"), '__for__': target},
        ])

    def test_render(self):
        result = self.call("{}", {'storage.files[0].path': "/foo.txt"})
        self.assertEqual(result[0], {'inline': "{}", '__for__': target})
        self.assertEqual(loads(result[1]['inline'])['storage'], {
            'files': [{'path': "/foo.txt"}],
        })

    def test_headers(self):
        headers = {"Authorization": "Basic secret"}
        result = self.call("{}", URL("https://bar.com/"), headers=headers)
        self.assertEqual(result, [{
            'inline': "{}",
            '__for__': target,
        }, {
            'source': URL("https://bar.com/"),
            'http_headers': [
                {'name': "Authorization", 'value': "Basic secret"},
            ],
            '__for__': target,
        }])

    def test_for(self):
        merge = self.call(Path("/var/foo.txt"), URL("https://bar.com/"))
        result = self.call(
            {'__for__': "storage.files[]", 'path': "/var/baz.txt"},
            *merge,
            {'systemd.units[0].name': "sshd.service"},
        )
        self.assertEqual(loads(result[0]['inline'])['storage'], {
            'files': [{'path': "/var/baz.txt"}],
        })
        self.assertEqual(result[1:3], merge)
        self.assertEqual(loads(result[3]['inline'])['systemd'], {
            'units': [{'name': "sshd.service"}],
        })
