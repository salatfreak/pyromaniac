from typing import Self, Any


class Signature:
    def __init__(self, code: str):
        self.code = code

    @classmethod
    def create(cls, code: str) -> Self:
        return cls(code)

    @classmethod
    def default(cls) -> Self:
        return cls("(*args, **kwargs)")

    def parse(self, *args, **kwargs) -> dict[str, Any]:
        return {}
