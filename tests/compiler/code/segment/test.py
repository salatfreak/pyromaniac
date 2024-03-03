from unittest import TestCase
from pathlib import PosixPath as Path
from pyromaniac.compiler.code.segment.errors import (
    SignatureSyntaxError,
    UnexpectedTokenError,
)
from pyromaniac.compiler.code.segment import segment


class TestSegment(TestCase):
    def setUp(self):
        self.comps = Path(__file__).parent.joinpath("components")

    def test_pure_yaml(self):
        doc, sig, python, yaml = self.segment("pure_yaml")
        self.assertIsNotNone(yaml)
        self.assertTupleEqual((doc, sig, python), (None, None, None))

    def test_pure_python(self):
        doc, sig, python, yaml = self.segment("pure_python")
        self.assertIsNotNone(python)
        self.assertTupleEqual((doc, sig, yaml), (None, None, None))

    def test_all(self):
        doc, sig, python, yaml = self.segment("all")
        self.assertIsNotNone(doc)
        self.assertIsNotNone(sig)
        self.assertIsNotNone(python)
        self.assertIsNotNone(yaml)
        self.assertTrue(python.splitlines()[8].startswith("message ="))
        self.assertTrue(yaml.splitlines()[13].startswith("storage.files"))

    def test_invalid_signature(self):
        with self.assertRaises(SignatureSyntaxError):
            self.segment("invalid_signature")

    def test_unexpected_token(self):
        with self.assertRaises(UnexpectedTokenError) as ctx:
            self.segment("unexpected_token")
        self.assertEqual(ctx.exception.line, 1)
        self.assertEqual(ctx.exception.token.string, ')')

    def segment(
        self, path: str
    ) -> tuple[str | None, str | None, str | None, str | None]:
        source = self.comps.joinpath(path).with_suffix(".pyro").read_text()
        return segment(source)
