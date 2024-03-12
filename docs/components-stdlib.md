---
parent: Components
nav_order: 80
---

# Standard Library
The standard library provides a default set of components that can be used in
every pyromaniac configuration. It contains components for configuration
rendering, loading and rendering templates, and adding file system nodes.

{% raw %}
## Create merge fields for inline, local, and/or remote configs
```python
merge(
    *configs: str | Path | URL | dict,  # configurations to create merge for
    headers: dict = {},                 # headers to add for URLs
)
```

The result is intended to be added as the `ignition.config.merge` field.

For strings, paths, and URLs the result of passing them to the *contents*
component is added to the merge. For dicts composite keys are expanded and they
are rendered to a string using butane. Empty dicts are ignored. The *headers*
dict is passed to the *contents* component only for URLs.

**Example:**
- Merge inline butane config with remote ignition file using authentication:
  `merge({'storage.files[0].path': "/my/file.txt"},
  URL("https://example.com/config.ign"), headers={"Authorization": "..."})`

## Load file from disk and render it using jinja if variables are supplied
```python
load(
    path: Path,   # path to file
    **vars: Any,  # variables to pass to jinja renderer
)
```

Jinja is only invoked if at least one variable is passed as keyword argument.

**Example:**
- Load and render text file: `load(_/"file.txt", name="Alice")`

## Load JSON from disk injecting variables using jinja
```python
load.json(
    path: Path,   # path to file
    **vars: Any,  # variables to pass to jinja renderer
)
```

Jinja is only invoked if at least one variable is passed as keyword argument.

Jinja expressions will be serialized before inserting them into the document.
You can therefore safely inject structured data into your JSON document without
worrying about breaking JSON syntax. To insert raw strings into your document,
use the *raw* filter as in `{"greeting": "Hello, {{ name | raw }}!"}`.

**Example:**
- Load and inject: `load.json(_/"file.json", name="Alice")`

## Load YAML from disk injecting variables using jinja
```python
load.yaml(
    path: Path,   # path to file
    **vars: Any,  # variables to pass to jinja renderer
)
```

Jinja is only invoked if at least one variable is passed as keyword argument.

Jinja expressions will be serialized before inserting them into the document.
You can therefore safely inject structured data into your YAML document without
worrying about breaking YAML syntax. To insert raw strings into your document,
use the *raw* filter as in `greeting: "Hello, {{ name | raw }}!"`.

**Example:**
- Load and inject: `load.yaml(_/"file.yml", name="Alice")`

## Load TOML from disk injecting variables using jinja
```python
load.toml(
    path: Path,   # path to file
    **vars: Any,  # variables to pass to jinja renderer
)
```

Jinja is only invoked if at least one variable is passed as keyword argument.

Jinja expressions will be serialized before inserting them into the document.
You can therefore safely inject structured data into your TOML document without
worrying about breaking TOML syntax. To insert raw strings into your document,
use the *raw* filter as in `greeting = "Hello, {{ name | raw }}!"`.

**Example:**
- Load and inject: `load.toml(_/"file.toml", name="Alice")`

## Wrap value in magic type for convenient member access and default handling
```python
magic(
    value: Any,  # any value to wrap
)
```

Recursively wraps dicts and lists to allow access to dict members via dot
notation.

When encountering non-existent array or dict keys a *Nothing* object will be
returned that in turn returns itself when indexed. The *Nothing* object is
falsy and therefore allows specifying default values using `or DEFAULT`.

Beware that everything other than dicts, lists, and non-existent keys are
returned as is: `magic({"foo": 42}).foo.bar` will still result in an
AttributeError because 42 has no attribute *bar*.

**Examples:**
- Dot notation: `magic({"foo": [{"bar": "baz"}]}).foo[0].bar`
- Default handling: `magic({"foo": "bar"}).baz.qux or "default"`

## Create file fields with specified content and file ownership
```python
file(
    path: Path,                               # path to create the file at in the final system
    content: str | Path | URL | dict = None,  # string, path, or URL source or a custom dict
    user: int | str = None,                   # user ID or name
    group: int | str | None = ...,            # group ID or name (defaults to the same as user)
    headers: dict = {},                       # map of request headers for URL contents
    **fields: Any,                            # additional fields to take over as they are
)
```

The result is intended to be added as an element to the `storage.files` list.

The *path* must be absolute unless the user name is specified, in which case
relative paths will be interpreted relative to the users default home
directory.

The *content* and *headers* arguments are passed through the *content*
component. The *user* and *group* arguments are passed through the *ownership*
component. See their documentation for further details.

**Examples**:
- Add inline file for root user: `file("/file.txt", "foo")`
- Add file from disk for "core" user in its home directory:
  `file("file.txt", Path(_/"file.txt"), "core")`

## Create file system link fields with specified ownership
```python
link(
    path: Path,                     # path to create the link at in the final system
    target: Path,                   # path to link to
    user: int | str = None,         # user ID or name
    group: int | str | None = ...,  # group ID or name (defaults to the same as user)
    **fields: Any,                  # additional fields to take over as they are
)
```

The result is intended to be added as an element to the `storage.links` list.

The *path* must be absolute unless the user name is specified, in which case
relative paths will be interpreted relative to the users default home
directory.

The *user* and *group* arguments are passed through the *ownership* component.
See its documentation for further details.

**Examples**:
- Add absolute hard link for root user:
  `link("/file.txt", "/other.txt", hard=True)`
- Add relative soft link for "core" user in its home directory:
  `link("bin", ".local/bin", "core")`

## Create directory fields with specified ownership
```python
directory(
    path: Path,                     # path to create the directory at in the final system
    user: int | str = None,         # user ID or name
    group: int | str | None = ...,  # group ID or name (defaults to the same as user)
    **fields: Any,                  # additional fields to take over as they are
)
```

The result is intended to be added as an element to the `storage.directories`
list.

The *path* must be absolute unless the user name is specified, in which case
relative paths will be interpreted relative to the users default home
directory.

The *user* and *group* arguments are passed through the *ownership* component.
See its documentation for further details.

**Examples:**
- Add absolute directory for root user: `directory("/dir")`
- Add read-only directory for "core" user in its home directory:
  `directory("dir", "core", mode=0o550)`

## Create directory with parents with specified ownership
```python
directories(
    base: Path,                     # path to create directories under in the final system
    path: Path,                     # path of directories to create
    user: int | str = None,         # user ID or name
    group: int | str | None = ...,  # group ID or name (defaults to the same as user)
    **fields: Any,                  # additional fields to take over as they are
)
```

The result is intended to be added as the `storage.directories` field.

The *base* must be absolute unless the user name is specified, in which case
relative paths will be interpreted relative to the users default home
directory. The *path* will be interpreted relative to the *base*.

Only the members of the *path* that are children of *base* will be created, not
*base* itself.

The *user* and *group* arguments are passed through the *ownership* component.
See its documentation for further details.

**Example:**
- Add user unit directory for "core" user:
  `directories(".", ".config/systemd/user", "core")`

## Add local directory tree with specified ownership
```python
tree(
    path: Path,                     # path to create the directory at in the final system
    local: Path,                    # local directory to copy files from
    user: int | str = None,         # user ID or name
    group: int | str | None = ...,  # group ID or name (defaults to the same as user)
    mode: bool = False,             # whether to copy permission bits from the original files
    overwrite: bool = False,        # whether to set the `overwrite` field on all nodes
)
```

The result is intended to be added as the `storage` field.

The *path* must be absolute unless the user name is specified, in which case
relative paths will be interpreted relative to the users default home
directory.

The *user* and *group* arguments are passed through the *ownership* component.
See its documentation for further details.

If *mode* is True, file permissions will be copied from the original files.

**Example:**
- Copy config directory to "core" user's home directory preserving permissions:
  `tree(".config", _/"config", "core", mode=True)`

## Create contents dict as required for files and in several other places
```python
contents(
  content: str | Path | URL | dict,  # string, path, or URL source or a custom dict
  headers: dict = {},                # map of request headers to add
  **fields: Any,                     # additional fields to take over as they are
)
```

Will contain an "inline", "local", or "source" field depending on whether the
*content* argument is a string, path, or URL. If *content* is a dict, all key
value pairs from it will be copied into the result instead, overriding headers
and other fields.

**Examples**:
- Specify contents inline: `contents("foo")`
- Specify local file: `contents(Path("/path/to/file.txt"))`
- Specify remote file: `contents(URL("http://..."), headers={"Accept": "..."})`

## Create ownership fields as required for file system nodes
```python
ownership(
    user: int | str = None,         # user ID or name
    group: int | str | None = ...,  # group ID or name
)
```

Integers are interpreted as user/group IDs and strings as user/group names. The
group defaults to be the same as the user. Explicitly passing None disables
setting the field in the result.

**Examples:**
- Set user and group name to "core": `ownership("core")`
- Set only user ID to 1000: `ownership(1000, None)`
{% endraw %}
