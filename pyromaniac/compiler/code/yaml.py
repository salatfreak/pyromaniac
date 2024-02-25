from typing import Self, Any


class Yaml:
    def __init__(self, code: str):
        self.code = code

    @classmethod
    def create(cls, code: str) -> Self:
        return cls(code)

    def execute(self, context: dict) -> Any:
        return {}
