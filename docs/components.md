---
nav_order: 40
has_children: true
has_toc: false
---

# Components
{% raw %}
*Pyromaniac* configurations are written as one or more potentially nested
components in a custom format that combines *YAML*, *Jinja*, and *Python*.
Except for the special meaning of *Jinja* control structures, any valid
*Butane* configuration is also an equivalent valid *Pyromaniac* component.
*Pyromaniac* can therefore be considered to be a superset of *Butane* in
practice.

A collection of built-in components are available to you by default. You can
read their documentation on the [Standard Library][stdlib] page or take a look
at [their source code][source] as inspiration for your own components.

Since *Pyromaniac* is implemented in and relies on *Python* as part of its
configuration format, *Python* terminology will be used to describe data
structures in this document: Indexed arrays will be called lists, associative
arrays will be called dicts, and the *null* value will be called `None`.

[stdlib]: components-stdlib.html
[source]: https://github.com/salatfreak/pyromaniac/tree/main/stdlib

## Component Sections
Components consist of up to 4 sections, each of them optional. *Python*-style
comments and newlines before and between the sections are ignored.

A component may be completely empty. According to the following rules, an empty
component will be interpreted as only having an (empty) *YAML* section and will
therefore evaluate to `None`. Such a component will not be suitable as a main
component which must evaluate to a dict.

First of all, components may start with a docstring describing their
functioning, inputs, and output. It only serves the purpose of documentation
and doesn't affect how the component's output is constructed. The docstring
must be a valid static Python string. It must not be a byte string or an
f-string. It is advisable to follow the *Python* convention of employing triple
quotes as your string delimiters.

Secondly, a signature may follow describing the input parameters with their
types and defaults. It must start with an opening parenthesis and end with a
closing one. Details about the syntax, semantics, and type coercion are
described on the [Signature Section][signature] page.

The next possible section is the *Python* code block. It starts with a line
containing exactly three dashes and may close with another such line. If the
*Python* code block is not closed, it must end in an expression whose result
the entire component will evaluate to. Details about the syntax and execution
context can be found on the [Python Section][python] page.

Except for when the component contains an unclosed *Python* code block, the
rest of the component constitutes the *YAML* section. The *YAML* section may
contain *Jinja* control structures that will be evaluated to produce the
component's final result. Details about the syntax and execution context can be
found on the [YAML Section][yaml] page.

A minimal yet pointless component containing all 4 sections looks as follows.
Like the empty component, it evaluates to `None`.

```python
""
()
---
---
```

[signature]: components-signature.html
[python]: components-python.html
[yaml]: components-yaml.html

## The Main Component
*Pyromaniac*'s entrypoint will be your main component. You can pass it via
standard input or read it from a file. For multi-component configurations, it 
is recommended to employ a component named *main.pyro* and specify a single
dot as the first positional command line parameter to *Pyromaniac*.

The result of the main component will be used to compile the final *Ignition*
file. All *Pyromaniac* cares about is that your main component evaluates to a
dict. Whether you define it in place, construct it by combining a bunch of
other components, load it from a *TOML* file, etc., is up to you. *Pyromaniac*
will finalize the result and feed it to *Butane* to produce the *Ignition*
output.

## Finalization
Before serializing your main component's result to *YAML* as input for
*Butane*, *Pyromaniac* will process it by executing the following steps.

*Pyromaniac* will expand all composite keys, raising an error if any
conflicting keys are encountered. `{"a.b": [{"c.d": 42}], "a.b[1]": 69}` will
be converted to `{'a': {'b': [{'c': {'d': 42}}, 69]}}`.

All keys starting with an underscore will recursively be stripped from the
dict. You may use them to carry metadata between your components.

Finally, the *variant* and *version* fields will be set to *fcos* and the
latest *Butane* version respectively, if they are not specified in your
configuration.

## Component Trees
You can organize your *Pyromaniac* components and files in arbitrarily nested
directories. Ideally, every directory should be self-contained i.e., its
components shouldn't reference any data from ancestor directories and instead
be parameterized through arguments defined in its signature. Directory and
component names must be valid *Python* identifiers.

*Pyromaniac* makes it easy to reference components and files relative to the
currently evaluated component using the global *_* (underscore) variable
available in both *Python* code blocks and the *YAML*/*Jinja* section. You'll
find more information about it on the [Python Section][python] page.
{% endraw %}
