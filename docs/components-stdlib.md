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
std.merge(
    *configs: str | Path | URL | dict,  # configurations to create merge for
    headers: dict = {},                 # headers to add for URLs
)
```

The result is intended to be added as the `ignition.config.merge` field.

For strings, paths, and URLs, the result of passing them to the *std.contents*
component is added to the merge. For dicts, composite keys are expanded, and
they are rendered to a string using butane. Empty dicts are ignored. The
*headers* dict is passed to the *contents* component only for URLs.

**Example:**
- Merge inline butane config with remote ignition file using authentication:
  `std.merge({'storage.files[0].path': "/my/file.txt"},
  URL("https://example.com/config.ign"), headers={"Authorization": "..."})`

## Load file from disk and render it using jinja if variables are supplied
```python
std.load(
    path: Path,   # path to file
    **vars: Any,  # variables to pass to jinja renderer
)
```

Jinja is only invoked if at least one variable is passed as keyword argument.

**Example:**
- Load and render text file: `std.load(_/"file.txt", name="Alice")`

## Load JSON from disk injecting variables using jinja
```python
std.load.json(
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
- Load and inject: `std.load.json(_/"file.json", name="Alice")`

## Load YAML from disk injecting variables using jinja
```python
std.load.yaml(
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
- Load and inject: `std.load.yaml(_/"file.yml", name="Alice")`

## Load TOML from disk injecting variables using jinja
```python
std.load.toml(
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
- Load and inject: `std.load.toml(_/"file.toml", name="Alice")`

## Wrap value in magic type for convenient member access and default handling
```python
std.magic(
    value: Any,  # any value to wrap
)
```

Recursively wraps dicts and lists to allow access to dict members via dot
notation.

When encountering non-existent array or dict keys, a *Nothing* object will be
returned that in turn returns itself when indexed. The *Nothing* object is
falsy and therefore allows specifying default values using `or DEFAULT`.

Beware that everything other than dicts, lists, and non-existent keys are
returned as is: `std.magic({"foo": 42}).foo.bar` will still result in an
AttributeError because 42 has no attribute *bar*.

**Examples:**
- Dot notation: `std.magic({"foo": [{"bar": "baz"}]}).foo[0].bar`
- Default handling: `std.magic({"foo": "bar"}).baz.qux or "default"`

## Create file fields with specified content and file ownership
```python
std.file(
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
relative paths will be interpreted relative to the user's default home
directory.

The *content* and *headers* arguments are passed through the *std.contents*
component. The *user* and *group* arguments are passed through the
*std.ownership* component. See their documentation for further details.

**Examples**:
- Add inline file for root user: `std.file("/file.txt", "foo")`
- Add file from disk for "core" user in its home directory:
  `std.file("file.txt", _/"file.txt", "core")`

## Create file system link fields with specified ownership
```python
std.link(
    path: Path,                     # path to create the link at in the final system
    target: Path,                   # path to link to
    user: int | str = None,         # user ID or name
    group: int | str | None = ...,  # group ID or name (defaults to the same as user)
    **fields: Any,                  # additional fields to take over as they are
)
```

The result is intended to be added as an element to the `storage.links` list.

The *path* must be absolute unless the user name is specified, in which case
relative paths will be interpreted relative to the user's default home
directory.

The *user* and *group* arguments are passed through the *std.ownership*
component. See its documentation for further details.

**Examples**:
- Add absolute hard link for root user:
  `std.link("/file.txt", "/other.txt", hard=True)`
- Add relative soft link for "core" user in its home directory:
  `std.link("bin", ".local/bin", "core")`

## Create directory fields with specified ownership
```python
std.directory(
    path: Path,                     # path to create the directory at in the final system
    user: int | str = None,         # user ID or name
    group: int | str | None = ...,  # group ID or name (defaults to the same as user)
    **fields: Any,                  # additional fields to take over as they are
)
```

The result is intended to be added as an element to the `storage.directories`
list.

The *path* must be absolute unless the user name is specified, in which case
relative paths will be interpreted relative to the user's default home
directory.

The *user* and *group* arguments are passed through the *std.ownership*
component. See its documentation for further details.

**Examples:**
- Add absolute directory for root user: `std.directory("/dir")`
- Add read-only directory for "core" user in its home directory:
  `std.directory("dir", "core", mode=0o550)`

## Create directory with parents with specified ownership
```python
std.directories(
    base: Path,                     # path to create directories under in the final system
    path: Path,                     # path of directories to create
    user: int | str = None,         # user ID or name
    group: int | str | None = ...,  # group ID or name (defaults to the same as user)
    **fields: Any,                  # additional fields to take over as they are
)
```

The result is intended to be added as the `storage.directories` field.

The *base* must be absolute unless the user name is specified, in which case
relative paths will be interpreted relative to the user's default home
directory. The *path* will be interpreted relative to the *base*.

Only the members of the *path* that are children of *base* will be created, not
*base* itself.

The *user* and *group* arguments are passed through the *std.ownership*
component. See its documentation for further details.

**Example:**
- Add user unit directory for "core" user:
  `std.directories(".", ".config/systemd/user", "core")`

## Add local directory tree with specified ownership
```python
std.tree(
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
relative paths will be interpreted relative to the user's default home
directory.

The *user* and *group* arguments are passed through the *std.ownership*
component. See its documentation for further details.

If *mode* is True, file permissions will be copied from the original files.

**Example:**
- Copy config directory to "core" user's home directory preserving permissions:
  `std.tree(".config", _/"config", "core", mode=True)`

## Create contents dict as required for files and in several other places
```python
std.contents(
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
- Specify contents inline: `std.contents("foo")`
- Specify local file: `std.contents(Path("/path/to/file.txt"))`
- Specify remote file:
  `std.contents(URL("http://..."), headers={"Accept": "..."})`

## Parse content string into inline, path or URL value based on its format
```python
std.contents.parse(
    content: str,  # path, URL, or inline content as string
)
```

Values starting with "/" or "./" will be returned as path objects. Values
starting with one of butanes supported protocol names followed by "://" will be
returned as URL objects. Everything else will be returned as is.

**Examples**:
- Inline content: `std.contents.parse("foo")`
- Local file: `std.contents.parse("./bar.txt")`
- Remote file: `std.contents.parse("https://example.com/baz.txt")`

## Create ownership fields as required for file system nodes
```python
std.ownership(
    user: int | str = None,         # user ID or name
    group: int | str | None = ...,  # group ID or name
)
```

Integers are interpreted as user/group IDs and strings as user/group names. The
group defaults to be the same as the user. Explicitly passing None disables
setting the field in the result.

**Examples:**
- Set user and group name to "core": `std.ownership("core")`
- Set only user ID to 1000: `std.ownership(1000, None)`
{% endraw %}
