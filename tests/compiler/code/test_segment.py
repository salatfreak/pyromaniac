from unittest import TestCase
from pathlib import PosixPath as Path
from pyromaniac.compiler.code.segment.errors import (
    InvalidSignatureError,
    UnexpectedTokenError,
)
from pyromaniac.compiler.code.segment import segment


class TestSegment(TestCase):
    def setUp(self):
        self.comps = Path(__file__).parent.parent.parent.joinpath("components")

    def test_pure_yaml(self):
        doc, sig, python, yaml = self.segment("qux")
        self.assertIsNotNone(yaml)
        self.assertTupleEqual((doc, sig, python), (None, None, None))

    def test_pure_python(self):
        doc, sig, python, yaml = self.segment("quux")
        self.assertIsNotNone(python)
        self.assertTupleEqual((doc, sig, yaml), (None, None, None))

    def test_all(self):
        doc, sig, python, yaml = self.segment("foo/baz")
        self.assertIsNotNone(doc)
        self.assertIsNotNone(sig)
        self.assertIsNotNone(python)
        self.assertIsNotNone(yaml)
        self.assertTrue(python.splitlines()[8].startswith("message ="))
        self.assertTrue(yaml.splitlines()[13].startswith("storage.files"))

    def test_invalid_signature(self):
        with self.assertRaises(InvalidSignatureError):
            self.segment("bar/main")

    def test_unexpected_token(self):
        with self.assertRaises(UnexpectedTokenError) as ctx:
            self.segment("bar/fred")
        self.assertEqual(ctx.exception.line, 1)
        self.assertEqual(ctx.exception.token.string, ')')

    def segment(
        self, path: str
    ) -> tuple[str | None, str | None, str | None, str | None]:
        source = self.comps.joinpath(path).with_suffix(".pyro").read_text()
        return segment(source)
