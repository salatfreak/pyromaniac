from unittest import TestCase
from os import chdir
from pathlib import PosixPath as Path
from json import loads
from pyromaniac.remote import Remote
from pyromaniac import compile


class TestAll(TestCase):
    def setUp(self):
        chdir(Path(__file__).parent.joinpath("components/all"))

    def test_all(self):
        main = Path("main.pyro").read_text()
        result = loads(compile(main, Remote("http", "example.com", 80, None)))
        self.assertIsInstance(result, dict)
