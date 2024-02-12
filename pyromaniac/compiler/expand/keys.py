def parse(key: str) -> list[str | int]:
    """Split a key string into its string and int parts.

    Turns e.g. "foo[0].bar" into ["foo", 0, "bar"].

    :param key: key string to split up
    :returns: list of key parts
    """
    parts = []
    for k in key.split('.'):
        if '[' in k and k.endswith(']'):
            name, indices = k[:-1].split('[', 1)
            parts.extend([name, *(int(i) for i in indices.split(']['))])
        else:
            parts.append(k)
    return parts


def format(parts: list[str | int]) -> str:
    """Formats key parts into a single key string.

    Turns e.g. ["foo", 0, "bar"] into "foo[0].bar"

    :param parts: list of key parts
    :returns: formatted key string
    """
    return "".join(
        f"[{k}]" if isinstance(k, int) else f".{k}"
        for k in parts
    )[1:]
