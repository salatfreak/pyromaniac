from unittest import TestCase
from unittest.mock import patch
from io import StringIO
from pathlib import PosixPath as Path
from pyromaniac.args import parse

from . import temp


class TestArgs(TestCase):
    def test_input(self):
        self.assertEqual(parse().input, Path("/dev/stdin"))
        args = parse(["-i", "/test.pyro"]).input
        self.assertEqual(args, Path("/test.pyro"))

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

    @temp.place("salt.hex")
    def test_address(self, salt_file: Path):
        self.assertEqual(parse().address, ('http', '127.0.0.1', 8000))

        with patch('pyromaniac.server.auth.SALT_FILE', salt_file):
            args = parse(["--address", "https://example.com/"])
            self.assertEqual(args.address, ("https", "example.com", 443))
            args = parse(["--address", "https://example.com:9000/"])
            self.assertEqual(args.address, ("https", "example.com", 9000))
        self.assertTrue(salt_file.exists())

    @temp.place("salt.hex")
    def test_auth(self, salt_file: Path):
        self.assertIsNone(parse().auth)
        self.assertEqual(parse(["--auth", "name:pass"]).auth, "name:pass")
        with patch('pyromaniac.server.auth.SALT_FILE', salt_file):
            args = parse(["--address", "https://example.com/"])
            self.assertTrue(args.auth.startswith("pyromaniac:"))

    def test_error(self):
        stderr = StringIO()
        with self.assertRaises(SystemExit), patch('sys.stderr', stderr):
            parse(["--address", "ftp://foo"])
        self.assertTrue(stderr.getvalue().startswith("Usage:"))
