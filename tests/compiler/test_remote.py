from unittest import TestCase
from unittest.mock import patch
from base64 import b64encode
from pathlib import PosixPath as Path
from pyromaniac.remote import Remote
from pyromaniac.compiler.url import URL
from ..temp import place


class TestRemote(TestCase):
    def test_create(self):
        remote = Remote.create(("http", "foo.bar", 8000), "none")
        self.assertIsNone(getattr(remote, "_Remote__auth"))
        remote = Remote.create(("http", "foo.bar", 8000), None)
        self.assertIsNone(getattr(remote, "_Remote__auth"))
        remote = Remote.create(("https", "foo.bar", 8000), None)
        self.assertEqual(getattr(remote, "_Remote__auth"), "auto")

    def test_url(self):
        remote = Remote.create(("https", "foo.com", 443), "secret")
        self.assertEqual(remote.url, URL("https://foo.com:443"))

    @place("salt.hex")
    def test_call(self, salt_file: Path):
        remote = Remote("https", "foo.com", 443, "secret")
        url = URL("https://foo.com:443/config.ign")
        keys = [
            'ignition.config.merge[0].source',
            'ignition.config.merge[0].http_headers',
            'ignition.security.tls.certificate_authorities[0].inline',
        ]
        with patch('pyromaniac.server.auth.SALT_FILE', salt_file):
            result = remote()
        self.assertEqual(set(result.keys()), set(keys))
        self.assertEqual(result[keys[0]], url)
        self.assertEqual(result[keys[1]], [{
            'name': "Authorization",
            'value': "Basic " + b64encode("secret".encode()).decode(),
        }])
        self.assertTrue(result[keys[2]].startswith('-----BEGIN CERTIFICATE'))
