from pathlib import PosixPath as Path
from tarfile import TarFile

from ..temp import dir
from .base import TestCase


class TestTree(TestCase):
    comp = 'std.tree'

    @dir
    def test_empty(self, tmp: Path):
        self.assertEqual(self.call("/dir", tmp), {
            'directories': [
                {'path': Path("/dir"), '__for__': 'storage.directories[]'}
            ],
            'files': [],
            'links': [],
            '__for__': 'storage',
        })

    @dir
    def test_full(self, tmp: Path):
        # unpack archive in temporary directory
        tar = TarFile.open(self.lib.view() / "tree.tar")
        tar.extractall(tmp, filter='tar')
        tar.close()
        local = tmp.joinpath("tree")

        # test construction of tree
        common = {'user': {'name': "alice"}, 'overwrite': True}
        self.assertEqual(self.call("dir", local, "alice", None, True, True), {
            'directories': [{
                'path': Path("/home/alice/dir"), 'mode': 0o755, **common,
                '__for__': 'storage.directories[]',
            }, {
                'path': Path("/home/alice/dir/foo"), 'mode': 0o510, **common,
                '__for__': 'storage.directories[]',
            }],
            'files': [{
                'path': Path("/home/alice/dir/foo/bar.sh"),
                'contents': {'local': local.joinpath("foo/bar.sh")},
                'mode': 0o755, **common,
                '__for__': 'storage.files[]',
            }],
            'links': [{
                'path': Path("/home/alice/dir/bar"),
                'target': Path("foo/bar.sh"),
                'mode': 0o777, **common,
                '__for__': 'storage.links[]',
            }],
            '__for__': 'storage',
        })
