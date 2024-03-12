from unittest import TestCase
from unittest.mock import patch
from io import StringIO
from pathlib import PosixPath as Path
from pyromaniac.args import parse

from . import temp


class TestArgs(TestCase):
    def test_input(self):
        self.assertEqual(parse().input, Path("/dev/stdin"))

        args = parse(["/foo.pyro"])
        self.assertEqual(args.input, Path("/foo.pyro"))
        self.assertEqual(args.args, [])

        self.assertEqual(parse(["."]).input, Path("main.pyro"))

    def test_args(self):
        args = parse(["/bar.pyro", "foo", "bar"])
        self.assertEqual(args.input, Path("/bar.pyro"))
        self.assertEqual(args.args, ["foo", "bar"])

    def test_butane_args(self):
        self.assertEqual(parse().butane, [])
        args = parse(["-p", "-s"]).butane
        self.assertEqual(args, ["--pretty", "--strict"])

    def test_mode(self):
        self.assertEqual(parse().mode, 'ign')
        self.assertEqual(parse(["--iso"]).mode, 'iso')
        self.assertEqual(parse(["--serve"]).mode, 'serve')

    def test_iso_net(self):
        self.assertIsNone(parse().iso_net)
        args = parse([
            "--iso-net", "client=192.168.0.2,netmask=255.255.255.0",
        ])
        self.assertEqual(args.iso_net, "192.168.0.2:::255.255.255.0::::::")

    def test_address(self):
        self.assertEqual(parse().address, ('http', '127.0.0.1', 8000))
        args = parse(["--address", "https://example.com/"])
        self.assertEqual(args.address, ("https", "example.com", 443))
        args = parse(["--address", "https://example.com:9000/"])
        self.assertEqual(args.address, ("https", "example.com", 9000))

    def test_installer(self):
        self.assertEqual(parse().installer, [])
        self.assertEqual(parse(["--iso-raw-force"]).installer, [("force",)])
        self.assertEqual(
            parse(["--iso-raw-pre-install", "foo"]).installer,
            [("pre-install", "foo")]
        )
        self.assertEqual(parse([
            "--iso-raw-ignition-ca", "bar",
            "--iso-raw-help",
        ]).installer, [
            ("ignition-ca", "bar"),
            ("help",),
        ])

    def test_error(self):
        stderr = StringIO()
        with self.assertRaises(SystemExit), patch('sys.stderr', stderr):
            parse(["--address", "ftp://foo"])
        self.assertTrue(stderr.getvalue().startswith("Usage:"))
