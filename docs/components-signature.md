---
parent: Components
nav_order: 20
---

# Signature Section
*Pyromaniac* component signatures specify the arguments accepted by your
components with their types and default values. They use the same syntax as
Python function signatures including variadic arguments, union types, etc. If
no signature is specified, it defaults to `(*args, **kwargs)` to accept any
number of positional and keyword arguments.

*Pyromaniac* will perform type checking and coercion at runtime. Calling a
component with arguments that don't match its signature will result in an
error.

In your signature specification, you have access to *Any* from the *typing*
module, *Path* for the *PosixPath* class from the *pathlib* module, and a
special *URL* class in addition to all of Python's built-in identifiers. The
*URL* class wraps a string in its *url* field and supports the slash operator
for concatenation with strings as in `URL("https://example.com") / "path.html"`
similar to the *Path* class. You may also use union types and a limited
selection of generics as described below.

The following is an example of a valid signature with some documentation.

```python
(
    title: str,  # the document title
    content: Path | URL,  # a path or URL the content should be loaded from
    sources: list[str | dict[str, str]] = [],  # an optional list of sources
    **meta: str,  # any number of meta tags
)
```

## Supported Types
You may use any built-in types and classes in your signatures, and *Pyromaniac*
will check if the passed arguments are instances of the specified types. If you
want to allow any type, use *Any* or omit the type annotation altogether.

To allow multiple types, you may use the pipe syntax as in `str | int`.
*Pyromaniac* will check the types from left to right and stop at the first
match. This becomes relevant when type coercion comes into play: A string can,
e.g., be coerced into a *Path* or *URL* but not the other way around. If you
annotate an argument with `str | Path`, it will work as expected. If you switch
the two around, you'll always end up with a Path.

The supported generics are `list[T]` to make sure all elements of the list are
of type `T`, `dict[TK, TV]` to make sure all dict keys are of type `TK` and
all values of type `TV`, and `tuple[TA, TB, TC, ...]` to make sure the tuple
has the specified amount and types of elements in the specified order. Other
generics are not supported and will raise errors.

*NoneType* and *EllipsisType* are not available in signatures, but you may use
`None` and `...` in your type annotations directly. You may also specify them
as default values, and *Pyromaniac* will add them to the supported types, so
`(name: str = None)` will turn into `(name: str | None = None)`. This is not
the case for other types.

## Type Coercion
In general, arguments must be instances of the type specified in the signature.
Some types support coercion, though.

Integers and floating-point numbers may be used interchangeably as long as they
are compatible: You may pass `3.0` as an integer argument but not `3.5`.

Strings will be coerced into *Path*s and *URL*s but not the other way around.

Tuples and lists may be passed interchangeably.

Other coercions will not take place.

## Passing Arguments to the Main Component
If your main component specifies a signature, you can pass arguments to it via
the command line. The first positional parameter to *Pyromaniac* will always
be the path to the main component. Any further positional parameters will
be passed to the main component according to its signature. These parameters
can themselves be either positional parameters or named in the long option
style (`--<name>=<value>` or `--<name> <value>`). If an option name appears
twice or more or the signature declares it as such, a list of values will be
passed to your component. The usual coercion rules apply, but additionally,
if the signature declares a primitive type (*bool*, *int*, or *float*),
*Pyromaniac* will try to convert the argument accordingly. For passing named
*bool* parameters, use either `--<name>=(true|false)` or the shorter form
`--<name>`/`--no-<name>`.

Let's consider a *main.pyro* component with the following signature.

```python
(
    timeout: int,
    host: str,
    mod: list[str] = [],
    debug: bool = False,
)
```

You could execute `pyromaniac . -- --mod vpn 60 --mod health --debug --
--my-host--` to populate the *mod* argument with the value `["vpn", "health"]`,
*timeout* with `60`, *debug* with `True`, and *host* with `"--my-host--"`. Note
that unlike in python function calls you can mix named and positional
parameters as long as the positional parameters appear in the right order. Also
note the `--` parameter being used twice: the first one to mark all following
parameters as positional to *Pyromaniac* (and thus to be used as arguments to
your component) and the second one to mark the last parameter as positional for
the component itself.

If the positional parameters don't match your main component's signature,
compilation will fail with an appropriate error message. It is recommended to
use arguments to main components sparingly and rather put custom configuration
into *TOML*, *YAML*, or *JSON* files that are read from within your components.
