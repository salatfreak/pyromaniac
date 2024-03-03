from typing import Self, Any
from traceback import format_exception
from ..errors import CompilerError


class CodeError(CompilerError):
    """Base class for code parsing and execution errors."""


class InvalidDocstringError(CodeError):
    """Error raised when component is not a static string."""

    def __init__(self):
        super().__init__("Component docstring is not a static string.")


class InvalidSignatureError(CodeError):
    """Error raised when signature specification is invalid."""

    @classmethod
    def unsupported_type(cls, type: str) -> Self:
        """Create signature error for unsupported type annotation.

        :param type: type annotation as string
        :returns: InvalidSignatureError with appropriate message
        """
        return cls(f'Unsupported type "{type}" in signature.')

    def message(self) -> str:
        err = self.__cause__
        if isinstance(err, SyntaxError):
            details = f": {repr(err.text.strip())}" if err.text else ""
            details += f" in line {err.lineno}" if err.lineno else ""
            return f"Syntax error in signature{details}."
        elif err is not None:
            message = str(err)
            return f"Invalid signature: {message[:1].upper()}{message[1:]}."
        else:
            return super().message()


class InvalidArgumentError(CodeError):
    """Error raised when invalid argument was passed to component."""

    @classmethod
    def wrong_type(cls, value: Any, type: str) -> Self:
        """Create argument error for wrong argument type.

        :param value: value passed to component
        :param type: type that was expected for parameter
        :returns: InvalidArgumentError with appropriate message
        """
        return cls(f"Expected argument {repr(value)} to be of type {type}.")

    @classmethod
    def wrong_count(cls, value: Any, count: int) -> Self:
        """Create argument error for wrong element count in tuple.

        :param value: value passed to component
        :param count: expected element count
        :returns: InvalidArgumentError with appropriate message
        """
        return cls(f"Expected tuple {value} to have {count} elements.")


class PythonError(CodeError):
    """Base class for errors in component python code."""


class PythonSyntaxError(PythonError):
    """Error raised when component python code has invalid syntax."""

    @classmethod
    def end_expression(cls) -> Self:
        """Create syntax error for component not ending with expression.

        :returns: PythonSyntaxError with appropriate message
        """
        return cls("Pure python component must end with an expression.")

    def message(self) -> str:
        err = self.__cause__
        if isinstance(err, SyntaxError):
            details = f": {repr(err.text.strip())}" if err.text else ""
            details += f" in line {err.lineno}" if err.lineno else ""
            return f"Syntax error in python code{details}."
        else:
            return super().message()


class PythonRuntimeError(PythonError):
    """Error raised when component python code raises error at runtime."""

    def message(self) -> str:
        err = self.__cause__
        trace = format_exception(type(err), err, err.__traceback__)
        return "".join(trace[2:]).rstrip()


class YamlError(CodeError):
    """Base class for errors in component yaml code."""


class YamlTemplateError(YamlError):
    """Error raised when jinja template is invalid."""

    def message(self) -> str:
        err = self.__cause__
        details = str(err) + f" in line {err.lineno}" if err.lineno else ""
        return f"Error in jinja template: {details[:1].upper()}{details[1:]}"


class YamlExecutionError(YamlError):
    """Error raised when rendering jinja template raises error."""

    def message(self) -> str:
        err = self.__cause__
        trace = format_exception(type(err), err, err.__traceback__)
        return "".join(trace[4:]).rstrip()


class YamlParseError(YamlError):
    """Error raised when rendered yaml code has invalid syntax."""

    def message(self) -> str:
        details = str(self.__cause__)
        if details.startswith("while"):
            return f"Encountered invalid YAML {details}"
        else:
            details = details[:1].upper() + details[1:]
            return f"Encountered invalid YAML:\n{details}"
