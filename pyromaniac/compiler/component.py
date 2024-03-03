from typing import Self, Any

from .code import parse, Signature, Python, Yaml


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

    def execute(
        self, ctx: dict, args: tuple = tuple(), kwargs: dict[str, Any] = {},
    ) -> Any:
        """Execute component with the given context and arguments.

        :param ctx: context to execute in
        :returns: result of the components execution
        """
        ctx.update(self.sig.parse(*args, **kwargs))
        if self.python is not None:
            self.python.execute(ctx)
        if self.yaml is None:
            return ctx['result']
        else:
            return self.yaml.execute(ctx)
