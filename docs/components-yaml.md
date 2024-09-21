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
(underscore). An extra `value is ellipsis` test is availlable in *Jinja*
templates to check if a value is `...` (the `Ellipsis`).

## Serialization of Jinja Expressions
Data from *Jinja* expressions will generally be *JSON* serialized before being
inserted into the *YAML* document, making use of the fact that *YAML* is a
superset of *JSON*. You can therefore safely inject complex data structures
produced by the *Python* section or by other components into your *YAML* code.

Use the `raw` filter to insert raw strings into your document as in ``name:
"`'Alice' | raw` Rodriguez"``.
