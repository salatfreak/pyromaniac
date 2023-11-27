root, local = (Path(arg) for arg in args)
user, group, mode = kwargs.get('user'), kwargs.get('group'), kwargs.get('mode')

# Common arguments and constructor
common = {}
TYPE_KEY = { int: 'id', str: 'name' }
if user is not None: common['user'] = { TYPE_KEY[type(user)]: user }
if group is not None: common['group'] = { TYPE_KEY[type(group)]: group }
def node(path, **kwargs):
    extra = { 'mode': path.lstat().st_mode % 0o10000 } if mode else {}
    path = path.relative_to(local)
    return { 'path': root / path, **common, **extra, **kwargs }

# Assemble butane config
dirs, files, links = [], [], []
for p in [local, *local.glob("**/*")]:
    if p.is_symlink(): links.append(node(p, target=p.readlink()))
    elif p.is_dir(): dirs.append(node(p))
    elif p.is_file(): files.append(node(p, contents={'local': p}))

{ 'storage': { 'directories': dirs, 'files': files, 'links': links } }
