from typing import Self, Any, Iterator
from keyword import iskeyword
from collections.abc import Mapping
from pathlib import PosixPath as Path

from .errors import CompilerError, NonExistentPathError, NotAComponentError
from .context import context
from .component import Component


def is_var_name(name: str):
    return name.isidentifier() and not iskeyword(name)


class Library(Mapping):
    """Library of files and components.

    :param root: root path for the library
    :param libs: list of libraries to merge into namespace
    """

    def __init__(self, root: Path, libs: list[Self] = []):
        self.root = root
        self.libs = libs
        self.cache = {}

    def resolve(self, name: str) -> tuple[Self, str] | None:
        path = self.get_path(name)
        if path.with_suffix(".pyro").is_file():
            return self, name
        elif path.joinpath("main.pyro").is_file():
            return self, f"{name}.main"
        return next(filter(None, (b.resolve(name) for b in self.libs)), None)

    def execute(
        self, name: str, args: tuple = tuple(), kwargs: dict[str, Any] = {}
    ) -> Any:
        comp = self.get_component(name)
        parent = name.rsplit(".", 1)[0] if "." in name else ""
        try:
            return comp.execute(context(self, self[parent]), args, kwargs)
        except CompilerError as e:
            raise e.push(name)

    def get_component(self, name: str) -> Component:
        path = self.get_path(name).with_suffix(".pyro")

        if name not in self.cache:
            try:
                self.cache[name] = Component.create(path.read_text())
            except CompilerError as e:
                raise e.push(name)

        return self.cache[name]

    def view(self) -> 'View':
        """Get root view on this library.

        :returns: root view on this library
        """
        return View(self, "")

    def get_path(self, name: str) -> Path:
        """Get file system path for specified name under this library.

        :param name: name to get path for
        :returns: file system path for the specified name
        """
        return self.root.joinpath(*name.split("."))

    # methods required by the abstract Mapping class
    def __getitem__(self, name: str) -> 'View':
        path = self.get_path(name)
        if (
            name == "" or
            path.with_suffix(".pyro").is_file() and is_var_name(path.name) or
            path.is_dir() and is_var_name(path.name) or
            any(lib.__contains__(name) for lib in self.libs)
        ):
            return View(self, name)
        else:
            raise KeyError(name)

    def __iter__(self) -> Iterator[str]:
        return iter(set(
            path.name if path.is_dir() else path.stem
            for path in self.root.iterdir()
            if path.suffix == '.pyro' and is_var_name(path.stem)
            or path.is_dir() and is_var_name(path.name)
        ).union(
            name for lib in self.libs for name in lib.keys()
        ))

    def __len__(self) -> int:
        return sum(1 for _ in iter(self))


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
        match self.__path, name:
            case p, '_' if "." in p: path = p.rsplit(".", 1)[0]
            case p, '_' if p != "": path = ""
            case "", n: path = n
            case p, n: path = f"{p}.{n}"

        if path != '_' and path in self.__lib:
            return View(self.__lib, path)

        raise NonExistentPathError(name)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Try to call the viewed path in the library as a component.

        :param args: arguments to pass to the component
        :param kwargs: keyword arguments to pass to the component
        :returns: result of the components execution
        """
        pair = self.__lib.resolve(self.__path)
        if pair is None:
            raise NotAComponentError(self.__path)
        return pair[0].execute(pair[1], args, kwargs)

    def __truediv__(self, other: str | Path) -> Path:
        return self.__lib.get_path(self.__path).joinpath(other)
