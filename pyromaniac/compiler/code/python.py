from typing import Self, Any


class Python:
    def __init__(self, code: str):
        self.code = code

    @classmethod
    def create(cls, code: str, final: bool) -> Self:
        return cls(code)

    def execute(self, context: dict) -> Any:
        return {}
