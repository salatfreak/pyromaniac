"""Generate stdlib component docs.

Running this in the pyromaniac container produces the docs source code for the
standard library:

.. code-block:: sh
   podman run --rm \
     --volume ./pyromaniac:/src/pyromaniac:ro \
     --volume ./stdlib:/usr/local/lib/pyromaniac/std:ro \
     --volume ./docs:/src/docs:ro \
     --workdir /src \
     --entrypoint "/usr/bin/python3" \
     pyromaniac docs/stdlib-docs.py \
       > docs/components-stdlib.md
"""

from pathlib import Path
from pyromaniac.compiler.code.segment import segment

ORDER = [
    'merge',
    'load', 'load.json', 'load.yaml', 'load.toml', 'magic',
    'file', 'link', 'directory', 'directories', 'tree',
    'contents', 'ownership',
]
STDLIB = Path("/", "usr", "local", "lib", "pyromaniac", "std")

print("""
---
parent: Components
nav_order: 80
---

# Standard Library
The standard library provides a default set of components that can be used in
every pyromaniac configuration. It contains components for configuration
rendering, loading and rendering templates, and adding file system nodes.
""".strip())

print("\n{% raw %}", end="")

for name in ORDER:
    file = STDLIB.joinpath(*name.split(".")).with_suffix(".pyro")
    doc, sig, _, _ = segment(file.read_text())
    doc, sig = doc.strip('"').strip(), sig.strip("\n")
    title, text = doc.strip().split("\n\n", 1)
    title, text = title.rstrip("."), text.strip()
    print(f"\n## {title}\n```python\nstd.{name}(\n{sig}\n)\n```\n\n{text}")

print("{% endraw %}")
