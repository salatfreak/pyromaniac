from typing import Self, Any
from types import EllipsisType
from inspect import Parameter
import inspect
from pathlib import PosixPath as Path

from .errors import InvalidSignatureError, InvalidArgumentError
from ..url import URL
from .type import Type


class Signature:
    """Component signature.

    :param sig: function signature object
    :param types: dict mapping parameter names to types
    """

    def __init__(self, sig: inspect.Signature, types: dict[str, Type]):
        self.sig = sig
        self.types = types

    @classmethod
    def create(cls, code: str) -> Self:
        """Create signature from source code.

        :param code: signature code enclosed in parantheses
        :returns: compiled signature object
        """
        context = {'Any': Any, 'Path': Path, 'URL': URL}
        try:
            exec(f"def func({code}): pass", context)
        except Exception as e:
            raise InvalidSignatureError() from e
        sig = inspect.signature(context['func'])
        types = {n: get_type(p) for n, p in sig.parameters.items()}
        return cls(sig, types)

    @classmethod
    def default(cls) -> Self:
        """Create default signature with *args and **kwargs.

        :returns: compiled signature object
        """
        return cls.create("*args, **kwargs")

    def parse(self, *args, **kwargs) -> dict[str, Any]:
        """Match arguments to signature and check and coerce types.

        :returns: dict with mapping of variable names to values
        """
        try:
            params = self.sig.bind(*args, **kwargs)
        except TypeError as e:
            raise InvalidArgumentError() from e
        params.apply_defaults()
        return {
            n: self.types[n].coerce(v)
            for n, v in params.arguments.items()
        }


# get expected type for parameter
def get_type(param: inspect.Parameter) -> Type:
    match param.kind, param.annotation, param.default:
        case Parameter.VAR_POSITIONAL, Parameter.empty, _:
            return Type.create(list)
        case Parameter.VAR_POSITIONAL, annotation, _:
            return Type.create(list[annotation])
        case Parameter.VAR_KEYWORD, Parameter.empty, _:
            return Type.create(dict[str, Any])
        case Parameter.VAR_KEYWORD, annotation, _:
            return Type.create(dict[str, annotation])
        case _, Parameter.empty, _:
            return Type.create(Any)
        case _, annotation, None:
            return Type.create(annotation | None)
        case _, annotation, EllipsisType():
            return Type.create(annotation | EllipsisType)
        case _, annotation, _:
            return Type.create(annotation)
