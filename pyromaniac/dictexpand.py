from . import utils
from .errors import RenderError

def expand(original):
    name = original.name if isinstance(original, utils.NamedDict) else 'object'

    # Expand everything to flat key-value pairs
    flat = []
    work = [(k, v) for k, v in original.items()]
    while len(work) > 0:
        key, value = work.pop(0)
        if isinstance(value, dict):
            for sub in value.keys(): work.append((f"{key}.{sub}", value[sub]))
        elif isinstance(value, list):
            for i, el in enumerate(value): work.append((f"{key}[{i}]", el))
        else:
            flat.append((parse_key(key), value))

    # Filter out keys starting with underscores
    flat = [
        (k, v) for k, v in flat
        if not any(isinstance(p, str) and p.startswith('_') for p in k)
    ]

    # Create expanded dictionary
    result = {}
    for key, value in sorted(flat, key=lambda k: k[0]):
        current = result
        for i, part in enumerate(key[:-1]):
            new = [] if isinstance(key[i+1], int) else {}
            if isinstance(current, list):
                if not part <= len(current):
                    key_str = '.'.join(str(k) for k in key[:i])
                    msg = f"index {part} out of range in {key_str}"
                    raise RenderError(name, msg)
                if len(current) == part: current.append(new)
            else:
                if not part in current: current[part] = new
            current = current[part]
        if isinstance(current, list):
            if key[-1] != len(current):
                key_str = '.'.join(str(k) for k in key[:-1])
                msg = f"index {key[-1]} out of range in {key_str}"
                raise RenderError(name, msg)
            current.append(value)
        else:
            current[key[-1]] = value

    # Return expanded dictionary
    return result

def parse_key(key):
    result = []
    for part in key.split('.'):
        if '[' in part:
            name, index = part.split('[')
            index = int(index[:-1])
            result.append(name)
            result.append(index)
        else:
            result.append(part)
    return result
