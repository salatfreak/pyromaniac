from ..base import TestCase


class TestPyHierarchy(TestCase):
    comp = 'std.py.hierarchy'

    def test_dict(self):
        self.assertEqual(
            self.call('storage', {'files': []}), {'storage': {'files': []}},
        )
        self.assertEqual(
            self.call('boot_device.luks.tpm2', True),
            {'boot_device': {'luks': {'tpm2': True}}},
        )

    def test_array(self):
        self.assertEqual(self.call('foo[]', "bar"), {'foo': ["bar"]})
        self.assertEqual(
            self.call('storage.files[]', {'path': "/var/bar.txt"}),
            {'storage': {'files': [{'path': "/var/bar.txt"}]}},
        )

    def test_weird(self):
        self.assertEqual(self.call('', "foo"), {'': "foo"})
        self.assertEqual(self.call('[]', "bar"), {'': ["bar"]})
        self.assertEqual(
            self.call('systemd.units[].name', "sshd.service"),
            {'systemd': {'units[]': {'name': "sshd.service"}}},
        )
