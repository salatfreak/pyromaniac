from typing import Any
from collections.abc import Iterable
from unittest import TestCase
from contextlib import contextmanager

from pyromaniac.compiler.expand.errors import KeyExpandError
from pyromaniac.compiler.expand.errors import DuplicateKeyError
from pyromaniac.compiler.expand.errors import MixedKeysError
from pyromaniac.compiler.expand.errors import MissingIndexError
from pyromaniac.compiler.expand import expand


# check if expanding changes value
def changed(value: Any, *args, **kwargs):
    return expand(value, *args, **kwargs) != value


class TestExpand(TestCase):
    def test_scalars(self):
        bools = [False, True]
        for v, c, f in zip([42, "foo", True, None, ...], bools, bools):
            self.assertFalse(changed(v, c, f))

    def test_empty(self):
        self.assertFalse(changed([]))
        self.assertFalse(changed({}))

    def test_non_composite(self):
        self.assertFalse(changed([1, 2, 3]))
        self.assertFalse(changed({"foo": 42, "bar": 0}))
        self.assertFalse(changed({
            "foo": {"bar": 5},
            "baz": [{"hello": "world"}, [1, 2, 3]],
        }))

    def test_composite(self):
        self.assertEqual(expand({
            "foo.bar[2]": -1,
            "foo": {"bar": [42], "bar[1]": 69},
            "foo.baz": {"qux[0].quux.corge": "grault"},
            "waldo": "fred",
        }), {
            "foo": {
                "bar": [42, 69, -1],
                "baz": {"qux": [{"quux": {"corge": "grault"}}]},
            },
            "waldo": "fred",
        })

    def test_clean(self):
        self.assertFalse(changed({"foo": {"bar": "baz", "qux": "quux"}}, True))
        self.assertFalse(changed({"_oo": {"_ar": "baz", "qux": "quux"}}))
        self.assertEqual(expand({"_foo": 42, "bar": [{"_baz": 69}]}, True), {})
        self.assertEqual(expand([{"_foo": 42}, {"bar._baz[0]": 69}], True), [])
        self.assertEqual(expand({
            "foo": "bar",
            "_baz.qux": {"_quux": "corge"},
            "grault._waldo": "fred",
            "grault": {"plugh": {"_xyzzy": "thud"}},
        }, True), {
            "foo": "bar",
        })

    def test_fcos(self):
        self.assertTrue(changed({"foo": "bar"}, False, True))
        self.assertTrue(changed({"foo": "bar", "variant": "foo"}, False, True))
        self.assertFalse(changed({
            "foo": "bar", "variant": "foo", "version": "bar"
        }, False, True))

    def test_duplicate(self):
        with self.assertKeyExpandError(DuplicateKeyError, "foo"):
            expand({"foo": {}, "foo.bar": True})
        with self.assertKeyExpandError(DuplicateKeyError, "foo.bar"):
            expand({"foo.bar": True, "foo": {"bar": True}})
        with self.assertKeyExpandError(DuplicateKeyError, "foo[0]"):
            expand({"foo": [42], "foo[0]": 69})
        with self.assertKeyExpandError(DuplicateKeyError, "foo"):
            expand({"foo": 42, "foo[0]": 69})

    def test_mixed_keys(self):
        with self.assertKeyExpandError(MixedKeysError, "foo"):
            expand({"foo[0].bar": True, "foo.baz.qux": False})
        with self.assertKeyExpandError(MixedKeysError, "foo"):
            expand({"foo": [{"bar": True}], "foo.baz.qux": False})

    def test_missing_index(self):
        with self.assertKeyExpandError(MissingIndexError, "foo[1]"):
            expand({"foo[0]": 42, "foo[2]": 69})
        with self.assertKeyExpandError(MissingIndexError, "foo[1]"):
            expand({"foo": [42], "foo[2]": 69})
        with self.assertKeyExpandError(MissingIndexError, "foo[0].bar[2]"):
            expand({"foo": [{"bar": [42, 69]}], "foo[0].bar[3].baz": 69})

    @contextmanager
    def assertKeyExpandError(
        self, type: KeyExpandError, key: str
    ) -> Iterable:
        with self.assertRaises(type) as ctx:
            yield ctx
        self.assertEqual(ctx.exception.key(), key)
