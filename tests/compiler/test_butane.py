from unittest import TestCase
from unittest.mock import patch, Mock
import json

from pyromaniac.compiler import RenderError
from pyromaniac.compiler.butane import butane, configure


@patch('sys.stderr', Mock())
class TestButane(TestCase):
    def test_configure(self):
        config = {'foo': "bar", 'variant': "fcos", 'version': "1.5.0"}
        self.assertEqual(len(butane(config).splitlines()), 1)
        configure(["--pretty"])
        self.assertGreater(len(butane(config).splitlines()), 1)
        configure(["--strict"])
        with self.assertRaises(RenderError):
            butane(config)

    def test_butane(self):
        config = {'variant': "fcos", 'version': "1.5.0"}
        self.assertIn("version", json.loads(butane(config))["ignition"])
