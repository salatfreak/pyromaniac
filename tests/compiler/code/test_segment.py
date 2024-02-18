from unittest import TestCase
from pathlib import Path
from pyromaniac.compiler.code.segment.errors import (
    InvalidSignatureError,
    UnexpectedTokenError,
)
from pyromaniac.compiler.code.segment import segment


class TestSegment(TestCase):
    def setUp(self):
        self.comps = Path(__file__).parent.parent.parent.joinpath("components")

    def test_pure_yaml(self):
        doc, sig, python, yaml = segment(self.load("qux.pyro"))
        self.assertIsNotNone(yaml)
        self.assertTupleEqual((doc, sig, python), (None, None, None))

    def test_pure_python(self):
        doc, sig, python, yaml = segment(self.load("quux.pyro"))
        self.assertIsNotNone(python)
        self.assertTupleEqual((doc, sig, yaml), (None, None, None))

    def test_all(self):
        doc, sig, python, yaml = segment(self.load("foo", "baz.pyro"))
        self.assertIsNotNone(doc)
        self.assertIsNotNone(sig)
        self.assertIsNotNone(python)
        self.assertIsNotNone(yaml)
        self.assertTrue(python.splitlines()[8].startswith("message ="))
        self.assertTrue(yaml.splitlines()[13].startswith("storage.files"))

    def test_invalid_signature(self):
        with self.assertRaises(InvalidSignatureError):
            segment(self.load("bar", "main.pyro"))

    def test_unexpected_token(self):
        with self.assertRaises(UnexpectedTokenError) as ctx:
            segment(self.load("bar", "fred.pyro"))
        self.assertEqual(ctx.exception.line, 1)
        self.assertEqual(ctx.exception.token.string, ')')

    def load(self, *path: str) -> str:
        return self.comps.joinpath(*path).read_text()
