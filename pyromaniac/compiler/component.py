from typing import Self, Any

from .context import Context


class Component:
    """Loaded and executable pyromaniac component."""

    def __init__(self, source: str):
        self.source = source

    @classmethod
    def create(cls, source: str) -> Self:
        """Parse source code and create component from it.

        :param source: component source code
        :returns: created component
        """
        return cls(source)

    def execute(self, context: Context, *args: Any, **kwargs: Any) -> Any:
        """Execute component with the given context and arguments.

        :param context: context to execute in
        :returns: result of the components execution
        """
        return {}
