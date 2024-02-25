from typing import Self, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..context import Context


class Yaml:
    def __init__(self, code: str):
        self.code = code

    @classmethod
    def create(cls, code: str) -> Self:
        return cls(code)

    def execute(self, context: 'Context') -> Any:
        return {}
