name, source = [*args, None][:2]
enabled, user = kwargs.get('enabled'), kwargs.get('user')
if not '.' in name: name = f"{name}.service"

from SystemdUnitParser import SystemdUnitParser

def system_unit(name, source, enabled):
    unit = { 'name': name }
    if enabled is not None: unit['enabled'] = enabled
    if isinstance(source, Path): unit['contents_local'] = source
    elif isinstance(source, str): unit['contents'] = source
    return { 'systemd.units[0]': unit }

def user_unit(name, source, enabled, user):
    if isinstance(source, Path): source = source.read_text()

    # Add directory path
    parts = ['.config', 'systemd', 'user']
    owner = { 'user.name': user, 'group.name': user }
    dirs = [
        { 'path': Path('/home', user, *parts[:i]), **owner }
        for i in range(1, len(parts) + 1)
    ]

    # Add unit file
    path = Path('/home', user, *parts, name)
    files = [{ 'path': path, 'contents': { 'inline': source }, **owner }]

    # Add wants and requires links
    links = []
    if enabled:
        wants = parse_deps('wanted', source)
        requires = parse_deps('required', source)
        link_paths = [
            *(path.parent / f"{u}.wants" / name for u in wants),
            *(path.parent / f"{u}.requires" / name for u in requires),
        ]
        for p in link_paths:
            dirs.append({ 'path': p.parent, **owner })
            links.append({ 'path': p, 'target': Path('..', name), **owner })

    # Create config
    storage = { 'directories': dirs, 'files': files, 'links': links } 
    return { 'storage': storage }

def parse_deps(typ, source):
    typ = f'{typ.capitalize()}By'
    unit = SystemdUnitParser()
    unit.read_string(source)
    deps = unit.get('Install', typ) if unit.has_option('Install', typ) else []
    if not isinstance(deps, str): deps = " ".join(deps)
    return [dep for dep in deps.split() if dep != ""]

# Create requested config type
common = [name, source, enabled]
user_unit(*common, user) if user is not None else system_unit(*common)
