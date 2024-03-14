---
parent: Components
nav_order: 30
---

# Python Section
{% raw %}
The *Python* code block allows you to write arbitrary python code, including
import statements, function and class definitions, etc. Any imports, variables,
functions, and classes that you define will also be available in the
*YAML*/*Jinja* section. You may therefore use the *Python* section to prepare
the environment for *Jinja*.

If the *Python* section isn't closed with a line containing exactly three
dashes, it must end in an expression that will determine the component's
result. This can be a variable name, function call, or any arbitrarily complex
python expression.

The following component takes two numbers and simply returns their sum.

```python
(a: float, b: float)
---
a + b
```

## Execution Context
The context *Python* is executed in comes with *Any* from the *typing* module,
*Path* for the *PosixPath* class of the *pathlib*, and the special *URL* class
pre-imported, just like in the signature.

It also contains the *butane* and *expand* functions for rendering
configurations. This is what the *merge* component of the standard library uses
to render sub-configurations into *Ignition* format and assemble the contents
for the `ignition.config.merge` field. 

The *butane* function simply takes a configuration as a dict, transforms it
into *Ignition* and returns the result as a string.

The *expand* function recursively performs expansion of composite keys in dicts
and lists and leaves all other values as they are. Lists and dicts nested inside
other data structures will not be modified. You can optionally pass a second
and third parameter to control further modifications to the input. If the
second parameter is `True`, keys starting with an underscore will recursively
be filtered out of the result. If the third parameter is *True*, the *variant*
and *version* fields required by *Butane* will be added if the input is a dict
with these fields missing.

Lastly, the *GLOBAL* variable is a dict, shared by all components throughout
the compilation of the configuration. Using global state is discouraged. Pass
state around using component arguments and return values instead whenever
possible.

## Referencing Components and Local Files
You can reference directories and components by their name and execute them
as if they were python functions. You can traverse the component tree using
dot notation. To execute the component *foo/bar/baz.pyro*, simply write
`foo.bar.baz()`. If a directory contains a component named *main.pyro*, you may
call it by referencing the directory itself, as long as no component with the
same name exists: `foo.bar.main()` and `foo.bar()` are equivalent as long as
there is no component *foo/bar.pyro*.

The components from the [standard library][stdlib] are in scope by default.

Use the *_* (underscore) from the global context to reference the directory the
current component lies in, or use it as a field name on a component/directory
to reference its ancestor: The *foo/bar/baz.pyro* component can execute
*foo/bar/qux.pyro* by calling `_.qux()` and *foo/quux.pyro* by calling
`_._.quux()`. Referencing `_._` at the root of the component tree will raise an
error. It is recommended to use relative references whenever possible to
simplify refactoring and to make component directories truly self-contained.

Components/directories may also be used for referencing other files by using
the slash syntax: Read a file *data.txt* from the component's directory by
writing `load(_/"file.txt")`, or from its parent by writing
`load(_._/"file.txt")`.

[stdlib]: components-stdlib.html

## Referencing Pure Python Files
If your project requires complex *Python* logic or you wish to share classes or
functions between multiple components, you may also want to outsource code into
regular *Python* source files and import them from inside your components just
like you would from other *Python* modules.

*Python* modules should be referenced relative to the current component's path
for the same reason as components and local files. To import *pkg/mod.py* from
the component *pkg/comp.pyro*, write `from . import mod`.
{% endraw %}
