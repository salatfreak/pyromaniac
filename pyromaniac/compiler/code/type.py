from typing import Any, Self, NoReturn
from types import NoneType, GenericAlias, UnionType
from pathlib import PosixPath as Path

from .errors import InvalidSignatureError, InvalidArgumentError
from ..url import URL


class Type:
    """Type specification for runtime time checking and coercion."""

    def __init__(self, type: object):
        self.typ = type

    def coerce(self, value: Any) -> Any:
        """Coerce value into type raising InvalidArgumentError when impossible.

        :param value: value to coerce
        :returns: coerced value
        """
        return value if isinstance(value, self.typ) else self.throw(value)

    def throw(self, value: Any) -> NoReturn:
        raise InvalidArgumentError.wrong_type(value, self.typ.__name__)

    @classmethod
    def create(cls, type: object) -> Self:
        """Create type object of appropriate subclass.

        :param type: type of check and coerce into
        :returns: type object of appropriate subclass
        """
        if type is Any:
            return TypeAny()
        if type is None or type is NoneType:
            return TypeNone()
        elif type is bool:
            return TypeBool()
        elif type is str:
            return TypeString()
        elif type is int or type is float:
            return TypeNumber(type)
        elif type is Path:
            return TypePath()
        elif type is URL:
            return TypeURL()
        elif type is list:
            return TypeGeneric.create(list[Any])
        elif type is tuple:
            return TypeGeneric.create(tuple[...])
        elif type is dict:
            return TypeGeneric.create(dict[Any, Any])
        elif isinstance(type, GenericAlias):
            return TypeGeneric.create(type)
        elif isinstance(type, UnionType):
            return TypeUnion(type)
        else:
            return cls(type)


class TypeAny(Type):
    def __init__(self):
        super().__init__(Any)

    def coerce(self, value: Any) -> Any:
        return value


class TypeNone(Type):
    def __init__(self):
        super().__init__(NoneType)


class TypeBool(Type):
    def __init__(self):
        super().__init__(bool)


class TypeString(Type):
    def __init__(self):
        super().__init__(str)


class TypeNumber(Type):
    def coerce(self, value: Any) -> int | float:
        match value:
            case bool():
                self.throw(value)
            case int() | float() if self.typ(value) == value:
                return self.typ(value)
            case _:
                self.throw(value)


class TypeStringLike(Type):
    def coerce(self, value: Any) -> Path:
        match value:
            case str():
                return self.typ(value)
            case _:
                return super().coerce(value)


class TypePath(TypeStringLike):
    def __init__(self):
        super().__init__(Path)


class TypeURL(TypeStringLike):
    def __init__(self):
        super().__init__(URL)


class TypeGeneric(Type):
    expected = -1

    def __init__(self, type: GenericAlias):
        if self.expected >= 0 and len(type.__args__) != self.expected:
            raise InvalidSignatureError.invalid_type(str(type))
        super().__init__(type.__origin__)
        self.subtypes = tuple(Type.create(t) for t in type.__args__)

    @classmethod
    def create(cls, type: GenericAlias) -> Self:
        if type.__origin__ is list:
            return TypeList(type)
        elif type.__origin__ is tuple:
            return TypeTuple(type)
        elif type.__origin__ is dict:
            return TypeDict(type)
        else:
            raise InvalidSignatureError.invalid_type(str(type))


class TypeList(TypeGeneric):
    expected = 1

    def coerce(self, value: Any) -> list:
        if isinstance(value, tuple):
            value = list(value)
        else:
            value = super().coerce(value)

        return [self.subtypes[0].coerce(v) for v in value]


class TypeTuple(TypeGeneric):
    def __init__(self, type: GenericAlias):
        super().__init__(type)
        if type.__args__ == (Ellipsis,):
            self.subtypes = None

    def coerce(self, value: Any) -> tuple:
        if isinstance(value, list):
            value = tuple(value)
        else:
            value = super().coerce(value)

        if self.subtypes is None:
            return value
        elif len(value) != len(self.subtypes):
            raise InvalidArgumentError.wrong_count(value, len(self.subtypes))
        else:
            return tuple(t.coerce(v) for t, v in zip(self.subtypes, value))


class TypeDict(TypeGeneric):
    expected = 2

    def coerce(self, value: Any) -> dict:
        return {
            self.subtypes[0].coerce(k): self.subtypes[1].coerce(v)
            for k, v in super().coerce(value).items()
        }


class TypeUnion(Type):
    def __init__(self, type: UnionType):
        super().__init__(type)
        self.subtypes = tuple(Type.create(t) for t in type.__args__)

    def coerce(self, value: Any) -> Any:
        for type in self.subtypes:
            try:
                return type.coerce(value)
            except InvalidArgumentError:
                pass

        self.throw(value)

    def throw(self, value: Any) -> NoReturn:
        raise InvalidArgumentError.wrong_type(value, str(self.typ))
