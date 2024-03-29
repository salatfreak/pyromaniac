from unittest import TestCase
from unittest.mock import patch, Mock
from pathlib import PosixPath as Path
from pyromaniac import paths
from pyromaniac.iso.customize import get_base_image, customize_base_image

from . import temp


class TestIso(TestCase):
    @temp.dir
    @patch('subprocess.run')
    def test_get_base_image(self, images: Path, run: Mock):
        # create files
        old = images / "test-1.x86_64.iso"
        iso = images / "test-2.x86_64.iso"
        old.write_text("old")
        old.with_suffix(".iso.sig").write_text("old")
        iso.write_text("new")

        # prepare mock subprocess.run
        run.return_value.returncode = 0
        run.return_value.stdout = iso.as_posix()

        # call function and check results
        with patch('pyromaniac.paths.images', images):
            self.assertEqual(get_base_image("x86_64"), iso)

        # check subprocess function call
        args = run.call_args.args
        self.assertEqual(args[0][:2], [paths.installer, "download"])

        # check file existence
        self.assertTrue(iso.exists())
        iso.unlink()
        self.assertFalse(any(images.iterdir()))

    @patch('subprocess.run')
    def test_customize_base_image_min(self, run: Mock):
        run.return_value.returncode = 0
        customize_base_image(None, "{}", None, None, [])
        args = run.call_args.args[0]
        self.assertEqual(args[:3], [paths.installer, "iso", "customize"])
        self.assertIn("--live-ignition", args)
        self.assertNotIn("--live-karg-append", args)
        self.assertNotIn("--dest-ignition", args)
        self.assertNotIn("--dest-device", args)

    @patch('subprocess.run')
    def test_customize_base_image_max(self, run: Mock):
        run.return_value.returncode = 0
        customize_base_image(None, "{}", "client=192.168.0.2", "/dev/vda", [
            ("dest-karg-append", "quiet"), ("force",),
        ])
        args = run.call_args.args[0]
        self.assertIn("--live-karg-append", args)
        self.assertIn("--dest-ignition", args)
        self.assertIn("--dest-device", args)
        self.assertNotIn("--live-ignition", args)
        self.assertIn(("--dest-karg-append", "quiet"), zip(args, args[1:]))
        self.assertIn("--force", args)
