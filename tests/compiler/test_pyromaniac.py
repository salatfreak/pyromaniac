from unittest import TestCase
from pyromaniac.compiler.url import URL
from pyromaniac.compiler.pyromaniac import Pyromaniac


class TestPyromaniac(TestCase):
    def setUp(self):
        self.pyromaniac = Pyromaniac(("https", "foo.com", 443), "secret")

    def test_url(self):
        self.assertEqual(self.pyromaniac.url, URL("https://foo.com:443"))

    def test_remote(self):
        self.assertEqual(self.pyromaniac.remote(), {
            'ignition.config.replace': {
                'source': URL("https://foo.com:443/config.ign"),
                'http_headers': [{
                    'name': "Authorization",
                    'value': "Basic secret",
                }],
            }
        })

        self.assertEqual(self.pyromaniac.remote("https://bar.com/", None), {
            'ignition.config.replace': {'source': "https://bar.com/"},
        })
