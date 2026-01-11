from unittest import TestCase

from pyromaniac.compiler.errors import CommandLineArgumentError
from pyromaniac.compiler.code.signature import Signature
from pyromaniac.compiler import commandline


class TestCommandLine(TestCase):
    def test_positional(self):
        sig = Signature.create("foo, bar: str, baz: int = 3, qux: Path = None")
        self.assertEqual(
            commandline.parse((), sig),
            ((), {}),
        )
        self.assertEqual(
            commandline.parse(("hello", "world", "-42"), sig),
            (("hello", "world", -42), {}),
        )
        self.assertEqual(
            commandline.parse(("hello", "world", "twelve", "/foo.txt", "excess"), sig),
            (("hello", "world", "twelve", "/foo.txt", "excess"), {}),
        )
        self.assertEqual(
            commandline.parse(("hello", "world", "--", "--baz", "69", "--quiet"), sig),
            (("hello", "world", "--baz", "69", "--quiet"), {}),
        )

    def test_options(self):
        sig = Signature.create("foo: float, bar: bool, baz: bool = True, qux: URL = 3")
        self.assertEqual(
            commandline.parse(("--foo", "3.14", "--no-bar", "--baz=true"), sig),
            ((), {'foo': 3.14, 'bar': False, 'baz': True})
        )
        self.assertEqual(
            commandline.parse(("--foo", "3.14", "--quux", "-42"), sig),
            ((), {'foo': 3.14, 'quux': "-42"})
        )
        with self.assertRaises(CommandLineArgumentError) as e:
            commandline.parse(("--foo", "3.14", "--qux"), sig)
        self.assertEqual(e.exception.name, 'qux')

    def test_lists(self):
        sig = Signature.create("foo: list[str], bar: int, baz: list[float]")
        self.assertEqual(
            commandline.parse(
                ("--foo", "hello", "42", "--baz", "3.14", "--baz", "0"), sig
            ),
            (("42",), {'foo': ["hello"], 'baz': [3.14, 0.0]})
        )
        self.assertEqual(
            commandline.parse(
                ("--oof", "hello", "--oof", "world", "--baz", "invalid"), sig
            ),
            ((), {'oof': ["hello", "world"], 'baz': ["invalid"]})
        )

    def test_var_args(self):
        sig = Signature.create("foo: int, *bar: float, **baz: Path")
        self.assertEqual(
            commandline.parse(("2", "0", "42", "--qux", "false"), sig),
            ((2, "0", "42"), {'qux': "false"})
        )
        self.assertEqual(
            commandline.parse(("--bar", "hello", "--baz", "42", "--baz", "2"), sig),
            ((), {'bar': "hello", 'baz': ["42", "2"]})
        )

    def test_positional_or_keyword_only(self):
        sig = Signature.create("foo: int, /, bar: float, *, baz: bool")
        self.assertEqual(
            commandline.parse(("42", "-3.14", "true"), sig),
            ((42, -3.14, "true"), {})
        )
        self.assertEqual(
            commandline.parse(("--foo", "42", "--bar", "-3.14", "--no-baz"), sig),
            ((), {'foo': "42", 'bar': -3.14, 'baz': False})
        )
        self.assertEqual(
            commandline.parse(("42", "--no-baz", "--", "--bar"), sig),
            ((42, "--bar"), {'baz': False})
        )
