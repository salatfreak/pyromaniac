from typing import Self, Any

from .code import parse, Signature, Python, Yaml
from .context import Context


class Component:
    """Loaded and executable pyromaniac component."""

    def __init__(
        self, doc: str, sig: Signature, python: Python, yaml: Yaml,
    ):
        self.doc = doc
        self.sig = sig
        self.python = python
        self.yaml = yaml

    @classmethod
    def create(cls, source: str) -> Self:
        """Parse source code and create component from it.

        :param source: component source code
        :returns: created component
        """
        return cls(*parse(source))

    def execute(self, context: Context, *args: Any, **kwargs: Any) -> Any:
        """Execute component with the given context and arguments.

        :param context: context to execute in
        :returns: result of the components execution
        """
        context.update(self.sig.parse(*args, **kwargs))
        if self.python is not None:
            self.python.execute(context)
        if self.yaml is None:
            return context['result']
        else:
            return self.yaml.execute(context)
