from typing import Self, Any
from ..errors import CompilerError


class CodeError(CompilerError):
    pass


class InvalidDocstringError(CodeError):
    pass


class InvalidSignatureError(CodeError):
    @classmethod
    def invalid_type(cls, type: str) -> Self:
        return cls(f"unspported type specification {type}")


class InvalidArgumentError(CodeError):
    @classmethod
    def wrong_type(cls, value: Any, type: str) -> Self:
        return cls(f"argument {value} is not of type {type}")

    @classmethod
    def wrong_count(cls, value: Any, count: int) -> Self:
        return cls(f"argument {value} should have {count} elements")


class PythonError(CodeError):
    pass


class PythonSyntaxError(PythonError):
    pass


class PythonRuntimeError(PythonError):
    pass


class YamlError(CodeError):
    pass


class YamlTemplateError(YamlError):
    pass


class YamlExecutionError(YamlError):
    pass


class YamlParseError(YamlError):
    pass
