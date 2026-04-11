---
parent: Components
nav_order: 40
---

# YAML Section
Unless the component has an unclosed *Python* section, it ends with a *YAML*
section that determines the component's result. It may evaluate to any valid
*YAML* value, including *None*, by leaving it empty.

*Jinja* directives may be used to dynamically generate the *YAML* content,
using the "\`" (backtick) as delimiter for expressions. *Jinja* will have
access to *Any*, *Path*, *URL*, all imports, variables, functions, and classes
from the *Python* section, as well as your component tree and the *_*
(underscore). The extra tests `value is series` and `value is ellipsis` are
available in *Jinja* templates to check if a value is an iterable that is
neither a string nor a mapping, or `...` (the `Ellipsis`) respectively. There
is also a `shell` filter for escaping (lists of) shell arguments, as in
`"find " + (["/usr", "-name", "$Recycle.Bin"] | shell)`.

## Serialization of Jinja Expressions
Data from *Jinja* expressions will generally be *JSON* serialized before being
inserted into the *YAML* document, making use of the fact that *YAML* is a
superset of *JSON*. You can therefore safely inject complex data structures
produced by the *Python* section or by other components into your *YAML* code.

Use the `raw` filter to insert raw strings into your document as in ``name:
"`'Alice' | raw` Rodriguez"``.

## Extension for Running Components/Functions
Especially when nesting calls to components, embedded *Python* expressions in
your *Jinja* code can become pretty hard to read. You can use *run* blocks to
specify the parameters to a component or other function as *YAML* sequences or
mappings. You simply write your parameter list or mapping as the body between a
{% raw %}`{% run my_component %}` and an `{% endrun %}`{% endraw %} block. In
the opening block, you can add additional positional and keyword arguments,
separated by commas, after the component/function name. They will be prepended
to the ones specified in the *YAML* body.

The following example creates a  [*std.merge*][merge] of two configurations
specified as a *YAML* sequence. HTTP headers (which have no actual use in this
example) are specified as keyword argument inside the *run* block. The first
config is just a normal nested *YAML* structure. The second one uses another
*run* block for the [*std.file*][file] component though. This time, the
positional parameters are specified in the opening block, and the *YAML* body
is used to add keyword arguments.

{% raw %}
```python
ignition.config.merge: {% run std.merge headers={'Authorization': "..."} %}
  - passwd.users[0]:
      name: core
      ssh_authorized_keys_local: [`_/"id_rsa.pub"`]
  - storage.files[0]: {% run std.file "/etc/config.toml", URL("http://...") %}
      user: core
      mode: 0o755
  {% endrun %}
{% endrun %}
```
{% endraw %}

[file]: components-stdlib.html#create-file-fields-with-specified-content-and-file-ownership
[merge]: components-stdlib.html#create-merge-fields-for-inline-local-andor-remote-configs