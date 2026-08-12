from typing import Any, cast
from inspect import Parameter
from contextlib import suppress

from pyromaniac.compiler.errors import CommandLineArgumentError
from pyromaniac.compiler.code.type import Type as Type, TypeNumber, TypeList
from pyromaniac.compiler.code.signature import Signature


def parse(
    cmdl_args: tuple, signature: Signature,
) -> tuple[tuple, dict[str, Any]]:
    """Parse command line options and convert to primitive types.

    Double-dash parameters and flags will be parsed and primitive types and
    lists will be converted according to the signature. Missing or excess
    parameters and non-primitive or unparsable values will be left untouched.
    Appropriate coersions and errors will occur during the execution of the
    component anyways.

    :param cmdl_args: command line arguments
    :param signature: component signature
    :returns: arguments parsed according to the signature
    """
    # split into positional args and options
    flags = set(k for k, v in signature.types.items() if v.typ is bool)
    args, kwargs = parse_options(cmdl_args, flags)

    # convert positional arguments
    pos_types = [
        signature.types[n] for n, p in signature.sig.parameters.items()
        if p.kind in (
            Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD
        )
    ]
    for i, (value, typ) in enumerate(zip(args, pos_types)):
        args[i] = convert_to_type(value, typ)

    # convert keyword arguments
    kwargs = cast(dict[str, Any], kwargs)
    kw_types = {
        n: signature.types[n] for n, p in signature.sig.parameters.items()
        if p.kind in (Parameter.POSITIONAL_OR_KEYWORD, Parameter.KEYWORD_ONLY)
    }
    for name, values in kwargs.items():
        match values, kw_types.get(name):
            case _, TypeList(subtypes=[subtype]):
                kwargs[name] = [convert_to_type(v, subtype) for v in values]
            case [value], Type() as typ:
                kwargs[name] = convert_to_type(value, typ)
            case [value], _:
                kwargs[name] = value

    return tuple(args), kwargs


# split command line options into positional and option arguments
def parse_options(
    cmdl_args: tuple, flags: set[str],
) -> tuple[list[str], dict[str, list[str]]]:
    i, args, kwargs = 0, [], {}
    while i < len(cmdl_args):
        # get arg and increment index
        arg = str(cmdl_args[i])
        i += 1

        # stop parsing options on "--"
        if arg == '--':
            break

        # store as positional if not an option
        if not arg.startswith("--"):
            args.append(arg)
            continue
        arg = arg[2:]

        # get key and value
        if arg in flags:
            key, value = arg, "true"
        elif arg.startswith("no-") and arg[3:] in flags:
            key, value = arg[3:], "false"
        elif "=" in arg:
            key, value = arg.split("=", 1)
        elif i < len(cmdl_args):
            key, value = arg, cmdl_args[i]
            i += 1
        else:
            raise CommandLineArgumentError(arg)

        # add keyword argument
        kwargs[key] = kwargs.get(key, []) + [value]

    return args + list(cmdl_args[i:]), kwargs


# convert argument to specified type or return it as is
def convert_to_type(value: str, typ: Type) -> Any:
    match typ:
        case Type(typ=t) if t is bool:
            if value.lower() == "true":
                return True
            elif value.lower() == "false":
                return False
        case TypeNumber(typ=t) if t is int:
            with suppress(ValueError):
                return int(value)
        case TypeNumber(typ=t) if t is float:
            with suppress(ValueError):
                return float(value)

    return value
