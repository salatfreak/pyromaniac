from typing import Any
from unittest import TestCase
from pathlib import Path
from pyromaniac.compiler.code.errors import (
    InvalidArgumentError, InvalidSignatureError,
)
from pyromaniac.compiler.url import URL
from pyromaniac.compiler.code.signature import Signature


class TestSignature(TestCase):
    def test_default_signature(self):
        sig = Signature.default()
        self.assertEqual(sig.parse(), {'args': [], 'kwargs': {}})
        self.assertEqual(sig.parse("foo", [42], bar={"baz": "qux"}), {
            'args': ["foo", [42]],
            'kwargs': {'bar': {'baz': 'qux'}}
        })

    def test_invalid(self):
        with self.assertRaises(InvalidSignatureError):
            Signature.create("foo: strint")
        with self.assertRaises(InvalidSignatureError):
            Signature.create("bar: int: str")
        with self.assertRaises(InvalidSignatureError):
            Signature.create("in: Any")

    def test_no_type(self):
        sig = Signature.create("foo")
        sig.parse("bar")
        with self.assertRaises(InvalidArgumentError):
            sig.parse()
        with self.assertRaises(InvalidArgumentError):
            sig.parse("bar", 42)

    def test_default(self):
        sig = Signature.create("foo: str = 'bar'")
        self.assertEqual(sig.parse(), {"foo": "bar"})
        self.assertEqual(sig.parse("baz"), {"foo": "baz"})

        sig = Signature.create("foo: str = None")
        self.assertEqual(sig.parse(), {"foo": None})
        self.assertEqual(sig.parse(None), {"foo": None})
        self.assertEqual(sig.parse("baz"), {"foo": "baz"})

        sig = Signature.create("foo: str = ...")
        self.assertEqual(sig.parse(), {"foo": ...})
        self.assertEqual(sig.parse(...), {"foo": ...})
        self.assertEqual(sig.parse("baz"), {"foo": "baz"})

    def test_any(self):
        self.assertCoercion('Any', "bar")
        self.assertCoercion('Any', {"baz": "qux"})

    def test_none(self):
        self.assertCoercion('None', None)
        self.assertRaisesInvalidArgument('None', 42)
        sig = Signature.create("foo: None")
        with self.assertRaises(InvalidArgumentError):
            sig.parse()

    def test_ellipsis(self):
        self.assertCoercion('Ellipsis', ...)
        self.assertRaisesInvalidArgument('Ellipsis', 42)
        sig = Signature.create("foo: ...")
        with self.assertRaises(InvalidArgumentError):
            sig.parse()

    def test_bool(self):
        self.assertCoercion('bool', True)
        self.assertRaisesInvalidArgument('bool', "bar")
        self.assertRaisesInvalidArgument('bool', None)

    def test_string(self):
        self.assertCoercion('str', "hello")
        self.assertRaisesInvalidArgument('str', 42)
        self.assertRaisesInvalidArgument('str', Path("/hello/world"))
        self.assertRaisesInvalidArgument('str', None)

    def test_int(self):
        self.assertCoercion('int', 42)
        self.assertCoercion('int', 69.0, 69)
        self.assertNotCoercion('int', 69.0)
        self.assertRaisesInvalidArgument('int', False)
        self.assertRaisesInvalidArgument('int', 3.14)
        self.assertRaisesInvalidArgument('int', 42j)

    def test_float(self):
        self.assertCoercion('float', 42.0)
        self.assertCoercion('float', 69, 69.0, True)
        self.assertNotCoercion('float', 69.0, 69)
        self.assertRaisesInvalidArgument('float', False)
        self.assertRaisesInvalidArgument('float', 42j)

    def test_path(self):
        path = "/hello/world"
        self.assertCoercion('Path', Path(path))
        self.assertCoercion('Path', path, Path(path), True)
        self.assertRaisesInvalidArgument('Path', URL(path))
        self.assertRaisesInvalidArgument('Path', 42)
        self.assertRaisesInvalidArgument('Path', None)

    def test_url(self):
        url = "https://example.com/hello/world"
        self.assertCoercion('URL', URL(url))
        self.assertCoercion('URL', url, URL(url), True)
        self.assertRaisesInvalidArgument('URL', Path(url))
        self.assertRaisesInvalidArgument('URL', 42)
        self.assertRaisesInvalidArgument('URL', None)

    def test_generic(self):
        with self.assertRaises(InvalidSignatureError):
            Signature.create("foo: set[str]")

    def test_list(self):
        self.assertCoercion('list', [], equality=True)
        self.assertCoercion('list', ["foo", 42, {}], equality=True)
        self.assertCoercion('list', ("foo", 42, {}), ["foo", 42, {}], True)
        self.assertCoercion('list[int]', [], equality=True)
        self.assertCoercion('list[int]', (42, 69.0), [42, 69], True)
        self.assertCoercion('list[str]', ["foo", "bar"], equality=True)
        self.assertCoercion(
            'list[Path]',
            ["/hello/world", Path("foo")], [Path("/hello/world"), Path("foo")],
            True,
        )

        self.assertRaisesInvalidArgument('list', {})
        self.assertRaisesInvalidArgument('list', None)
        self.assertRaisesInvalidArgument('list[str]', [42])

        with self.assertRaises(InvalidSignatureError):
            Signature.create("foo: list[str, int]")

    def test_tuple(self):
        path, url = "/hello/world", "https://example.com/hello/world"
        self.assertCoercion('tuple', ())
        self.assertCoercion('tuple[...]', ("foo", 42, {}), equality=True)
        self.assertCoercion('tuple', ["foo", 42, {}], ("foo", 42, {}), True)
        self.assertCoercion('tuple[int]', (42,), equality=True)
        self.assertCoercion('tuple[int, int]', [42, 69.0], (42, 69), True)
        self.assertCoercion('tuple[str, float]', ("foo", 42), equality=True)
        self.assertCoercion(
            'tuple[Path, URL]', (path, url), (Path(path), URL(url)), True,
        )

        self.assertRaisesInvalidArgument('tuple', {})
        self.assertRaisesInvalidArgument('tuple', None)
        self.assertRaisesInvalidArgument('tuple[str]', [42])
        self.assertRaisesInvalidArgument('tuple[str]', ["foo", "bar"])

    def test_dict(self):
        path, url = "/hello/world", "https://example.com/hello/world"
        self.assertCoercion('dict', {}, equality=True)
        self.assertCoercion('dict', {"foo": 42, "bar": {}}, equality=True)
        self.assertCoercion('dict[str, str]', {}, equality=True)
        self.assertCoercion('dict[int, float]', {42: 69.0}, {42: 69}, True)
        self.assertCoercion(
            'dict[Path, URL]', {path: url}, {Path(path): URL(url)}, True,
        )

        self.assertRaisesInvalidArgument('dict', [])
        self.assertRaisesInvalidArgument('dict', None)
        self.assertRaisesInvalidArgument('dict[str, float]', {"foo", "bar"})
        self.assertRaisesInvalidArgument('dict[int, str]', {"foo", "bar"})

        with self.assertRaises(InvalidSignatureError):
            Signature.create("foo: dict[str]")
        with self.assertRaises(InvalidSignatureError):
            Signature.create("foo: dict[str, int, float]")

    def test_union(self):
        self.assertCoercion('str | int', "foo")
        self.assertCoercion('str | int', 42.0, equality=True)
        self.assertCoercion('str | Path', 'foo')
        self.assertCoercion('Path | str', 'foo', Path('foo'), True)
        self.assertCoercion('str | Path | URL', "foo")
        self.assertCoercion('str | Path | URL', Path("foo"))
        self.assertCoercion('str | Path | URL', URL("foo"))
        self.assertCoercion('str | int | float', 42)
        self.assertCoercion('str | str | dict', {"foo": "bar"}, equality=True)

        self.assertNotCoercion('str | float | int', 42)

        self.assertRaisesInvalidArgument('int | str', 3.14)
        self.assertRaisesInvalidArgument('int | str', None)

        with self.assertRaises(InvalidSignatureError):
            Signature.create("foo: int | dict[str]")
        with self.assertRaises(InvalidSignatureError):
            Signature.create("foo: int | dict[str]")

    def test_other(self):
        self.assertCoercion('set', {"foo", "bar"})

        self.assertRaisesInvalidArgument('set', {"foo": "bar"})
        self.assertRaisesInvalidArgument('set', None)

        with self.assertRaises(InvalidSignatureError):
            Signature.create("test: set[str]")

    def test_complex(self):
        sig = Signature.create("""
            foo: int | str,
            bar,
            baz: dict[Path, list[tuple[str, float | bool]]] = None,
            qux: Any = Path("lol"),
            **quux,
        """)

        self.assertEqual(sig.parse(42, object), {
            "foo": 42, "bar": object,
            "baz": None, "qux": Path("lol"), "quux": {}
        })

        self.assertEqual(sig.parse(
            "foo", "bar", {
                "baz": [("qux", True), ("quux", 69)],
            }, URL("corge"), fred="waldo",
        ), {
            "foo": "foo", "bar": "bar",
            "baz": {Path("baz"): [("qux", True), ("quux", 69.0)]},
            "qux": URL("corge"), "quux": {"fred": "waldo"},
        })

        with self.assertRaises(InvalidArgumentError):
            sig.parse(3.5, None)

        with self.assertRaises(InvalidArgumentError):
            sig.parse("foo", "bar", {42: []})

        with self.assertRaises(InvalidArgumentError):
            sig.parse("foo", "bar", {Path("baz"): [("qux", "quux")]})

    # assertion helpers
    def assertCoercion(
        self, type: str, val: Any, res: Any = ..., equality: bool = False
    ):
        if res is Ellipsis:
            res = val
        sig = Signature.create(f"foo: {type}")
        if equality:
            self.assertEqual(sig.parse(val)['foo'], res)
        else:
            self.assertIs(sig.parse(val)['foo'], res)

    def assertNotCoercion(
        self, type: str, val: Any, res: Any = ..., equality: bool = False
    ):
        if res is Ellipsis:
            res = val
        sig = Signature.create(f"foo: {type}")
        if equality:
            self.assertNotEqual(sig.parse(val)['foo'], res)
        else:
            self.assertIsNot(sig.parse(val)['foo'], res)

    def assertRaisesInvalidArgument(self, type: str, input: Any):
        sig = Signature.create(f"foo: {type}")
        with self.assertRaises(InvalidArgumentError):
            sig.parse(input)
