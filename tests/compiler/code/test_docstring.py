from unittest import TestCase
from pyromaniac.compiler.code.errors import InvalidDocstringError
from pyromaniac.compiler.code.docstring import parse


class TestDocstring(TestCase):
    def test_normal(self):
        self.assertEqual(parse('"foo bar"'), "foo bar")
        self.assertEqual(parse("'baz qux'"), "baz qux")
        self.assertEqual(parse('"""fred waldo"""'), "fred waldo")

    def test_prefixed_strings(self):
        self.assertEqual(parse('r"corge waldo"'), "corge waldo")
        self.assertEqual(parse('u"baz fred"'), "baz fred")

    def test_multiline_strings(self):
        self.assertEqual(len(parse(r'"hello\nworld"').splitlines()), 2)
        self.assertEqual(len(parse('''u"""
            This string
            has five lines
            in total.
         """''').splitlines()), 5)

    def test_wrong_type(self):
        self.assertRaisesInvalidDocstring("None")
        self.assertRaisesInvalidDocstring("42")
        self.assertRaisesInvalidDocstring('["bar"]')

    def test_invalid_string(self):
        self.assertRaisesInvalidDocstring('b"bar qux"')
        self.assertRaisesInvalidDocstring('f"bar qux"')

    def assertRaisesInvalidDocstring(self, code: str):
        with self.assertRaises(InvalidDocstringError):
            parse(code)
