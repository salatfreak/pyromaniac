from typing import Any, NoReturn, cast
from types import EllipsisType, GenericAlias, NoneType, UnionType
from pathlib import PosixPath as Path

from .errors import InvalidSignatureError, InvalidArgumentError
from ..url import URL


class Type:
    """Type specification for runtime time checking and coercion."""

    def __init__(self, typ: type | UnionType):
        self.typ = typ

    def coerce(self, value: Any) -> Any:
        """Coerce value into type raising InvalidArgumentError when impossible.

        :param value: value to coerce
        :returns: coerced value
        """
        return value if isinstance(value, self.typ) else self.throw(value)

    def throw(self, value: Any) -> NoReturn:
        name = self.typ.__name__ if isinstance(self.typ, type) else str(self.typ)
        raise InvalidArgumentError.wrong_type(value, name)

    @classmethod
    def create(cls, typ: object) -> 'Type':
        """Create type object of appropriate subclass.

        :param typ: type of check and coerce into
        :returns: type object of appropriate subclass
        """
        if typ is Any:
            return TypeAny()
        elif typ is None or typ is NoneType:
            return Type(NoneType)
        elif typ is Ellipsis or typ is EllipsisType:
            return Type(EllipsisType)
        elif typ is int or typ is float:
            return TypeNumber(typ)
        elif typ is Path or typ is URL:
            return TypeStringLike(typ)
        elif typ is list:
            return TypeGeneric.create_generic(cast(GenericAlias, list[Any]))
        elif typ is tuple:
            return TypeGeneric.create_generic(cast(GenericAlias, tuple[...]))  # type: ignore
        elif typ is dict:
            return TypeGeneric.create_generic(cast(GenericAlias, dict[Any, Any]))
        elif isinstance(typ, GenericAlias):
            return TypeGeneric.create_generic(typ)
        elif isinstance(typ, UnionType):
            return TypeUnion(typ)
        elif isinstance(typ, type):
            return cls(typ)
        else:
            raise InvalidSignatureError.unsupported_type(str(typ))


class TypeAny(Type):
    def __init__(self):
        super().__init__(Any)

    def coerce(self, value: Any) -> Any:
        return value


class TypeNumber(Type):
    typ: type[int | float]

    def coerce(self, value: Any) -> int | float:
        match value:
            case bool():
                self.throw(value)
            case int() | float() if self.typ(value) == value:
                return self.typ(value)
            case _:
                self.throw(value)


class TypeStringLike(Type):
    typ: type[Path | URL]

    def coerce(self, value: Any) -> Path | URL:
        match value:
            case str():
                return self.typ(value)
            case _:
                return super().coerce(value)


class TypeGeneric(Type):
    typ: GenericAlias
    expected = -1

    def __init__(self, typ: GenericAlias):
        assert isinstance(typ.__origin__, type)
        if self.expected >= 0 and len(typ.__args__) != self.expected:
            raise InvalidSignatureError.unsupported_type(str(typ))
        super().__init__(typ.__origin__)
        self.subtypes = tuple(Type.create(t) for t in typ.__args__)

    @classmethod
    def create_generic(cls, typ: GenericAlias) -> 'TypeGeneric':
        if typ.__origin__ is list:
            return TypeList(typ)
        elif typ.__origin__ is tuple:
            return TypeTuple(typ)
        elif typ.__origin__ is dict:
            return TypeDict(typ)
        else:
            raise InvalidSignatureError.unsupported_type(str(typ))


class TypeList(TypeGeneric):
    expected = 1

    def coerce(self, value: Any) -> list:
        if isinstance(value, tuple):
            value = list(value)
        else:
            value = super().coerce(value)

        return [self.subtypes[0].coerce(v) for v in value]


class TypeTuple(TypeGeneric):
    def __init__(self, typ: GenericAlias):
        super().__init__(typ)
        if typ.__args__ == (Ellipsis,):
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
    def __init__(self, typ: UnionType):
        super().__init__(typ)
        self.subtypes = tuple(Type.create(t) for t in typ.__args__)

    def coerce(self, value: Any) -> Any:
        for typ in self.subtypes:
            try:
                return typ.coerce(value)
            except InvalidArgumentError:
                pass

        self.throw(value)

    def throw(self, value: Any) -> NoReturn:
        raise InvalidArgumentError.wrong_type(value, str(self.typ))
