from unittest import TestCase
from unittest.mock import patch, Mock
from pathlib import PosixPath as Path
import json

from pyromaniac.compiler import ButaneError, NotADictError
from pyromaniac.compiler.butane import butane, configure


@patch('sys.stderr', Mock())
class TestButane(TestCase):
    def test_configure(self):
        config = {'foo': "bar", 'variant': "fcos", 'version': "1.5.0"}
        self.assertEqual(len(butane(config).splitlines()), 1)
        configure(["--pretty"])
        self.assertGreater(len(butane(config).splitlines()), 1)
        configure(["--strict"])
        with self.assertRaises(ButaneError):
            butane(config)

    def test_butane(self):
        config = {'variant': "fcos", 'version': "1.5.0"}
        self.assertIn("version", json.loads(butane(config))["ignition"])

    def test_path(self):
        config = {
            'variant': "fcos", 'version': "1.5.0",
            'storage': {'files': [{'path': Path("/foo/bar")}]},
        }
        ignition = json.loads(butane(config))
        self.assertEqual(ignition["storage"]["files"][0]["path"], "/foo/bar")

    def test_not_a_dict_error(self):
        with self.assertRaises(NotADictError):
            butane([])
