from typing import Any, Self
import re

from ..errors import PyromaniacError


class CompilerError(PyromaniacError):
    """Base for all component errors with component call stack.

    :param stack: list of component names
    """

    def __init__(self, *args, stack: list[str] = []):
        super().__init__(*args)
        self.stack = stack

    def push(self, component: str) -> Self:
        """Push a component name onto the stack.

        :param component: name of the component
        :returns: self for convenience
        """
        self.stack.append(component)
        return self

    def stack_message(self) -> str:
        """Generate an error message prefix based on the component stack.

        :returns: a message about the stack or an empty string if stack empty
        """
        match self.stack:
            case []:
                return ""
            case _:
                message = "Failed to execute component"
                stack = " from ".join(f'"{n}"' for n in self.stack)
                return f"{message} {stack}:"

    def __str__(self) -> str:
        match self.stack_message():
            case "": return self.message().lstrip()
            case str(stack): return f"{stack}\n{self.message()}"

    def message(self) -> str:
        """Create the error message for a compiler error.

        This should be overriden by subclasses to generate custom errors and
        will be prefixed with the component call stack by the compiler errors
        __str__ method.

        :returns: the created error message
        """
        if self.__cause__ is not None:
            message = str(self.__cause__)
            return message[:1].upper() + message[1:] + "."
        else:
            return super().__str__()


class NonExistentPathError(CompilerError, AttributeError):
    """Error raised when non-existent component path is accessed.

    :param path: path that was accessed
    """

    def __init__(self, path: str):
        super().__init__()
        self.path = path

    def message(self) -> str:
        path = repr(self.path)
        return f'Tried to access non-existent component path {path}.'


class NotAComponentError(CompilerError):
    """Error raised when directory is attempted to be executed as component.

    :param path: path that was attempted to be executed
    """

    def __init__(self, path: str):
        super().__init__()
        self.path = path

    def message(self) -> str:
        return f"Tried to execute non-existent component {repr(self.path)}."


class RenderError(CompilerError):
    """Base class for component rendering errors."""


class NotADictError(RenderError):
    """Error raised when trying to render component that returned non-dict.

    :param result: value returned by the component"""

    def __init__(self, result: Any):
        super().__init__()
        self.result = result

    def message(self) -> str:
        return (
            "Rendering component failed because it returned "
            f"{repr(self.result)} instead of a dictionary."
        )


class ButaneError(RenderError):
    """Error raised when rendering butane to ignition failed.

    :param error: butanes error output
    :param code: source yaml that was fed to butane
    """

    SURROUND_RE = re.compile(
        r'^(?:Error translating config: (?:yaml: unmarshal errors:)?)'
        '?(.*?)'
        '(?:Error translating config: config generated was invalid)?$',
        re.DOTALL,
    )
    LINE_RE = re.compile("^line (0|[1-9][0-9]*): (.*)$", re.DOTALL)

    def __init__(self, error: str, code: str):
        super().__init__()
        self.error = error
        self.code = code

    def message(self) -> str:
        error = self.SURROUND_RE.fullmatch(self.error)[1].strip()
        match = self.LINE_RE.fullmatch(error)
        if match:
            line = self.code.splitlines()[int(match[1]) - 1].strip()
            message = match[2]
            message = message[:1].upper() + message[1:]
            error = f'{message} in the line "{line}"'
        else:
            error = error[:1].upper() + error[1:]

        return f"Translating assembled config to ignition failed:\n{error}"
