# Pyromaniac: Creating Ignition with a Splash of Insanity
Pyromaniac is a Python and Jinja powered extension of [Butane][butane] and can
be used for modular and DRY configuration of [Fedora CoreOS][fcos] deployments.

[butane]: https://coreos.github.io/butane/
[fcos]: https://docs.fedoraproject.org/en-US/fedora-coreos/

## Building
1. Ensure [podman][podman] is installed.
2. Use `podman build -t pyromaniac .` to build the image.

[podman]: https://podman.io/

## Usage
The usage is similar to the *quay.io/coreos/butane* image. Use `bin/pyromaniac`
to conveniently run the image with the current directory mounted into the
container. This allows loading additional components easily. The `-e`, `--env`,
and `--env-file` parameters are passed to podman and can be used to set
environment variables. The rest of the parameters are passed to butane. Using
`bin/pyromaniac-debug` will additionally mount the source code into the
container, avoiding the need for constant rebuilds during development.

The program reads a pyromaniac config from stdin and writes the compiled
[Ignition][ignition] file to stdout.

[ignition]: https://coreos.github.io/ignition/

## Configuration format
Pyromaniac configuration files are Python scripts ending in an expression that
evaluates to a dictionary structured like a [Butane
configuration][butane-config] file. Converting your Butane YAML configuration
to JSON and adapting it to Python syntax by replacing `true`, `false`, and
`null` accordingly should therefore produce a valid pyromaniac configuration.
The *variant* and *version* fields default to *fcos* and *1.5.0*, respectively,
and can therefore be omitted.

You can leverage the full power of the Python programming language in these
configuration files and use the following additional features for convenience.

[butane-config]: https://coreos.github.io/butane/config-fcos-v1_5/

### Components
`bin/pyromaniac` mounts the current working directory into the container,
letting you load additional components. Reference them by their file system
path, using dots as delimiters and omitting the *.py* file extension. If the
file is named *main.py*, you may omit the file name entirely. To load and
execute a component *foo/bar/baz/main.py*, call `foo.bar.baz(*args, **kwargs)`.
In nested component trees, siblings can be referenced under the underscore
variable. Instead of calling `foo.bar.qux()` from inside *foo/corge.py*, you
can also call `_.bar.qux()`.

Positional and keyword arguments will be accessible to the component in the
*args* and *kwargs* variables.

Components may execute arbitrary Python code and produce arbitrary data. They
must, however, end with a standalone Python expression that will become the
component's return value.

A set of default components that produce valid pyromaniac configs is always
loaded and can be found in the *components* directory of this repository:

- `merge(*configs)`
  - compiles each non-`None` config to ignition format and creates a merge.
- `tree(path, local, user=, group=, mode=)`
  - Similar to *storage.trees* but with permission specification.
  - *user* and *group* are an optional id (integer) or name (string).
  - *mode* is an optional boolean and enables copying of permission bits.
- `unit(name, source, enabled=, user=)`
  - Similar to *systemd.units[0]* but with support for user units.
  - *source* is either a `Path()` or the unit content as a string.
  - *user* is an optional id (integer) or name (string).
- `linger(user)`
  - Enables services of the user named *user* to start at boot.

### Utils
Use `load(path)`, `json(path)`, and `yaml(path)` to load plain text, JSON, or
YAML data from a file, respectively.

Use `jinja(path, **kwargs)` to load and render a Jinja template from a file. It
will receive the data passed as keyword arguments.

Use `render(config)` to render a dictionary using Butane. The result will be a
string containing the Ignition JSON data, which can, for example, be used with
*ignition.config.merge.inline*. Fields starting with an underscore will be
filtered out. You can use them to pass data between your components.

To use file names relative to the current component, use `_/"file.txt"`.

Access environment variables using `env['VAR_NAME']`.

The `Path` class from `pathlib` comes pre-imported.

### Dictionary key expansion
Shorten nested data structures using composite keys with the familiar dot and
square bracket syntax (`foo.bar[0].baz`).

# Example
The following set of files produces an Ignition file for a system with an
*ext4* root partition and an example systemd unit running for the *core* user.
Compile it using
`bin/pyromaniac -e SSH_KEY="$(< ~/.ssh/id_rsa.pub)" < main.py > config.ign`.

*main.py*
```py
merge(
  rootfs('ext4'),
  core.main(env['SSH_KEY']),
)
```

*rootfs.py*
```py
fmt = args[0]

{
    'storage.filesystems[0]': {
        'device': "/dev/disk/by-label/root",
        'wipe_filesystem': True,
        'format': fmt,
        'label': 'root',
    }
}
```

*sshkey.py*
```py
user, keys = args

identify = { 'uid': user } if isinstance(user, int) else { 'name': user }
if isinstance(keys, str): keys = [keys]

{
  'passwd.users[0]': { **identify, 'ssh_authorized_keys': keys },
}
```

*core/main.py*
```py
key = args[0]

user = 'core'
merge(
    sshkey(user, key),
    tree(f"/home/{user}/bin", _/"bin", user=user, mode=True),
    linger(user),
    _.service(user, desc='Special Service'),
)
```

*core/bin/example.sh*
```sh
#!/bin/bash
echo 'hello world' > ~/greeting.txt
```

*core/service.py*
```py
user, desc = args[0], kwargs.get('desc', 'Example Service')

content = jinja(_/"example.service", desc=desc)
unit('example', content, enabled=True, user=user)
```

*core/example.service*
```ini
[Unit]
Description={{desc}}

[Service]
Type=oneshot
ExecStart=%h/bin/example.sh

[Install]
WantedBy=default.target
```
