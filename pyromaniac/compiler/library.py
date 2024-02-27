from typing import Self, Any
from keyword import iskeyword
from pathlib import PosixPath as Path

from .errors import NotAComponentError
from .context import Context
from .component import Component


def is_var_name(name: str):
    return name.isidentifier() and not iskeyword(name)


class Library:
    """Library of files and components.

    :param root: root path for the library
    :param libs: list of libraries to merge into namespace
    """

    def __init__(self, root: Path, libs: list[Self] = []):
        self.root = root
        self.libs = libs
        self.cache = {}

    def __contains__(self, key: str) -> bool:
        """Check if library contains given key as directory or component.

        :param key: dot-separated key to look up
        :returns: whether the key is contained
        """

        path = self.get_path(key)
        return path.with_suffix(".pyro").is_file() or path.is_dir() or any(
            lib.__contains__(key) for lib in self.libs
        )

    def dir(self) -> set[str]:
        """Create a set of directory and component names at the library root.

        :returns: set of names
        """
        return set(
            path.name if path.is_dir() else path.stem
            for path in self.root.iterdir()
            if path.suffix == '.pyro' and is_var_name(path.stem)
            or path.is_dir() and is_var_name(path.name)
        ).union(
            name for lib in self.libs for name in lib.dir()
        )

    def resolve(self, name: str) -> tuple[Self, str] | None:
        path = self.get_path(name)
        if path.with_suffix(".pyro").is_file():
            return self, name
        elif path.joinpath("main.pyro").is_file():
            return self, f"{name}.main"

        for lib in self.libs:
            result = lib.resolve(name)
            if result is not None:
                return result

    def execute(self, name: str, *args: Any, **kwargs: Any) -> Any:
        parent = name.rsplit(".", 1)[0] if "." in name else ""
        context = Context(self, self.view(parent), self.get_path(parent))
        comp = self.get(name)
        return comp.execute(context, *args, **kwargs)

    def get(self, name: str) -> Component | None:
        path = self.get_path(name).with_suffix(".pyro")

        if name not in self.cache:
            if not path.is_file():
                return None
            self.cache[name] = Component.create(path.read_text())

        return self.cache[name]

    def view(self, path: str = "") -> 'View':
        """Create a view on the library at a given path.

        :param path: dot-separated path to view the library from
        :returns: view on the library
        """
        return View(self, path)

    def get_path(self, name: str) -> Path:
        return self.root.joinpath(*name.split("."))


class View:
    """View on the library at a given path.

    Allows traversing the library with attribute notation. Uses "_" to traverse
    back to the parent.
    """

    def __init__(self, lib: Library, path: str = ""):
        self.__lib = lib
        self.__path = path

    def __getattr__(self, name: str) -> Self:
        """Get the view relative to this one at the given name."

        :param name: relative name to view the library from
        :returns: new view on the library
        """
        if name == '_':
            if self.__path != "":
                return View(self.__lib, ["", *self.__path.rsplit(".", 1)][-2])
        else:
            path = f"{self.__path}.{name}".lstrip(".")
            if path in self.__lib:
                return View(self.__lib, path)

        raise AttributeError(name)

    def __contains__(self, key: str) -> bool:
        """Check if library can be traversed from this view with the given key.

        :param key: key to check for
        :returns: whether traversal is possible
        """
        return self.__lib.__contains__(f"{self.__path}.{key}".lstrip("."))

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Try to call the viewed path in the library as a component.

        :param args: arguments to pass to the component
        :param kwargs: keyword arguments to pass to the component
        :returns: result of the components execution
        """
        pair = self.__lib.resolve(self.__path)
        if pair is None:
            message = f'"{self.__path}" is not the name of a component'
            raise NotAComponentError(message)
        return pair[0].execute(pair[1], *args, **kwargs)
