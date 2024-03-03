from typing import Any
from unittest import TestCase
from unittest.mock import patch
from os import chdir
from runpy import run_module
from pathlib import PosixPath as Path


@patch('sys.stdout.write')
def run(*args) -> tuple[Any, str]:
    *args, stdout = args
    ret = 0
    with patch('sys.argv', ["pyromaniac", *args]):
        try:
            run_module('pyromaniac')
        except SystemExit as e:
            ret = e.args[0]
    return ret, "".join(a.args[0] for a in stdout.call_args_list)


class TestModule(TestCase):
    def setUp(self):
        chdir(Path(__file__).parent.joinpath("components"))

    def test_help(self):
        ret, out = run("--help")
        self.assertEqual(ret, 0)
        self.assertNotEqual(out, "")

    def test_non_existent(self):
        ret, out = run("bananenbrot.pyro")
        self.assertIn("main component", ret)
        self.assertEqual(out, "")

    def test_empty(self):
        ret, out = run("empty.pyro")
        self.assertIn("returned None", ret)
        self.assertEqual(out, "")

    def test_minimal(self):
        ret, out = run("minimal.pyro")
        self.assertEqual(ret, 0)
        self.assertNotEqual(out, "")
