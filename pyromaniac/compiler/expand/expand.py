from typing import Any
from .errors import KeyExpandError
from .errors import DuplicateKeyError, MixedKeysError, MissingIndexError
from . import keys

FCOS_DEFAULTS = {'variant': "fcos", 'version': "1.6.0"}
FlatType = list[tuple[list[str | int], Any]]


def expand(config: Any, clean: bool = False, fcos: bool = False) -> Any:
    """Expand composite keys into hierarchy and add defaults.

    :param config: value with potentially composite keys
    :param clean: filter out keys starting with underscore
    :param fcos: apply FCOS default fields if config is a dict
    :returns: expanded config
    """
    flat = flatten(config)
    if clean:
        # clean and use original type if no keys left
        flat = clean_flat(flat) or [([], type(config)())]

    expanded = collect(flat)
    if isinstance(expanded, dict) and fcos:
        expanded = {**FCOS_DEFAULTS, **expanded}

    return expanded


def flatten(value: Any) -> FlatType:
    match value:
        case dict() if len(value) > 0:
            return [
                ([*keys.parse(k), *ks], v)
                for k, item in value.items()
                for ks, v in flatten(item)
            ]
        case list() if len(value) > 0:
            return [
                ([i, *ks], v)
                for i, item in enumerate(value)
                for ks, v in flatten(item)
            ]
        case _:
            return [([], value)]


def clean_flat(flat: FlatType) -> FlatType:
    return [
        (ks, v) for ks, v in flat
        if not any(isinstance(k, str) and k.startswith("_") for k in ks)
    ]


def collect(pairs: FlatType) -> Any:
    # handle empty key
    if any(p[0] == [] for p in pairs):
        if len(pairs) == 1:
            return pairs[0][1]
        else:
            raise DuplicateKeyError()

    # sort if int keys and detect mixed key types
    if all(isinstance(p[0][0], int) for p in pairs):
        pairs = sorted(pairs, key=lambda p: p[0][0])
    elif not all(isinstance(p[0][0], str) for p in pairs):
        raise MixedKeysError()

    # group pairs by first key part without reordering
    groups = {}
    for pair in pairs:
        groups[pair[0][0]] = [*groups.get(pair[0][0], []), pair]
    groups = list(groups.items())

    # handle string keys
    if isinstance(groups[0][0], str):
        result = {}
        for pre, ps in groups:
            try:
                result[pre] = collect([(k[1:], v) for k, v in ps])
            except KeyExpandError as e:
                raise e.under(pre)
        return result

    # handle int keys
    else:
        result = []
        for i, (pre, ps) in enumerate(groups):
            if i != pre:
                raise MissingIndexError([i])
            try:
                result.append(collect([(k[1:], v) for k, v in ps]))
            except KeyExpandError as e:
                raise e.under(pre)
        return result
