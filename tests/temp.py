from typing import Callable, Any
from pathlib import Path
from tempfile import TemporaryDirectory


def dir(func: Callable) -> Callable:
    """Decorate function for creating temporary directory.

    Creates a temporary directory for the lifetime of the function and passes
    it a Path to that directory as an additional parameter.

    :param func: function to decorate
    :returns: decorated function
    """
    def wrapper(*args, **kwargs) -> Any:
        with TemporaryDirectory() as temp:
            return func(*args, Path(temp), **kwargs)
    return wrapper


def place(name: str = "file") -> Callable[[Callable], Callable]:
    """Create a decorator for creating temporary empty places for a files.

    Creates a temporary directory for the lifetime of the function and passes
    it a non-existent path in it with the given name as an additional
    parameter.

    :param name: name for the Path inside the temporary directory
    :returns: function decorator
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args) -> Callable[..., Any]:
            with TemporaryDirectory() as temp:
                return func(*args, Path(temp, name))
        return wrapper
    return decorator


def file(
    name: str = "file", content: str | bytes | None = None
) -> Callable[[Callable], Callable]:
    """Create a decorator for creating temporary files.

    Creates a temporary directory with a file in it for the lifetime of the
    function and passes it a Path to the file as an additional parameter.

    :param name: name for the file
    :param content: content to initialize the file with
    :returns: function decorator
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args) -> Callable[..., Any]:
            with TemporaryDirectory() as temp:
                path = Path(temp, name)
                if isinstance(content, str):
                    path.write_text(content)
                elif isinstance(content, bytes):
                    path.write_bytes(content)
                return func(*args, path)
        return wrapper
    return decorator
