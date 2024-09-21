from .base import TestCase


class TestOwnership(TestCase):
    comp = 'std.ownership'

    def test_defaults(self):
        self.assertEqual(self.call(), {})
        self.assertEqual(self.call("core"), {
            'user': {'name': "core"}, 'group': {'name': "core"},
        })
        self.assertEqual(self.call("core", None), {'user': {'name': "core"}})

    def test_types(self):
        self.assertEqual(self.call(1001, "alice"), {
            'user': {'id': 1001}, 'group': {'name': "alice"},
        })
        self.assertEqual(self.call("bob", 1002), {
            'user': {'name': "bob"}, 'group': {'id': 1002},
        })
