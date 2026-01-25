from .base import TestCase


class TestPython(TestCase):
    comp = 'std.py.merge'

    def test_primitive(self):
        self.assertEqual(self.call(42), 42)
        self.assertEqual(self.call({"foo": "bar"}), {"foo": "bar"})
        self.assertEqual(self.call(42, "foo", None), None)

    def test_mixed(self):
        self.assertEqual(self.call({"foo": 42}, 69), 69)
        self.assertEqual(self.call(69, "foo", {"bar": -1}), {"bar": -1})
        self.assertEqual(self.call({"foo": 42}, [69, -1], merge_lists=True), [69, -1])

    def test_dicts(self):
        d1 = {"a": {"b": 1, "c": [2, 3]}, "d": 4}
        d2 = {"a": {"b": 5}, "e": 6}
        d3 = {"a": {"c": [7]}, "d": 8}
        self.assertEqual(self.call(d1, d2, d3), {
            "a": {"b": 5, "c": [7]}, "d": 8, "e": 6
        })
        self.assertEqual(self.call(d1, d2, d3, merge_lists=True), {
            "a": {"b": 5, "c": [2, 3, 7]}, "d": 8, "e": 6
        })