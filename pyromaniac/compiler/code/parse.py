from .segment import segment
from .docstring import parse as docstring_parse
from .signature import Signature
from .python import Python
from .yaml import Yaml


def parse(
    code: str,
) -> tuple[str | None, Signature, Python | None, Yaml | None]:
    """Parse component code and return compiled code segments.

    :param code: component source code
    :returns: tuple with doc string, signature, and compiled python and yaml
    """
    doc, sig, python, yaml = segment(code)
    return (
        docstring_parse(doc) if doc is not None else None,
        Signature.create(sig) if sig is not None else Signature.default(),
        Python.create(python, yaml is None) if python is not None else None,
        Yaml.create(yaml) if yaml is not None else None,
    )
