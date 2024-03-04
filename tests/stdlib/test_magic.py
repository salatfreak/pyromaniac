from .base import TestCase


class TestMagic(TestCase):
    comp = 'magic'

    def test_primitives(self):
        self.assertIs(self.call(True), True)
        self.assertIs(self.call(42), 42)
        self.assertIs(self.call("foo"), "foo")

    def test_object(self):
        obj = object()
        self.assertIs(self.call(obj), obj)

    def test_dict(self):
        wrapped = self.call({"foo": {"bar": [{"baz": 42}]}})
        self.assertIsInstance(wrapped, dict)
        self.assertEqual(wrapped.foo.bar[0].baz, 42)
        self.assertEqual(wrapped.foo.bananenbrot.__class__.__name__, 'Nothing')
        self.assertEqual(wrapped.foo.bar.qux[42].quux or 69, 69)
        with self.assertRaises(AttributeError):
            wrapped.foo.bar[0].baz.qux

    def test_list(self):
        wrapped = self.call([{"foo": "bar"}, "baz", 42])
        self.assertEqual(wrapped[0].foo or "qux", "bar")
        self.assertEqual(wrapped[2], 42)
        self.assertEqual(wrapped[42].foo or 69, 69)
