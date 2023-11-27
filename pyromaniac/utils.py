import sys
import subprocess
from pathlib import PosixPath
from json import load as json_load, JSONDecodeError
from yaml import safe_load as yaml_load, dump as yaml_dump
from yaml import add_representer, YAMLError
import jinja2

from .dictexpand import expand
from .errors import LoadError, RenderError

BUTANE_DEFAULTS = {
    'variant': 'fcos',
    'version': '1.5.0',
}

JINJA_ENV = jinja2.Environment()

def load(src):
    src = PosixPath(src)
    try: return src.read_text()
    except IOError as e: raise LoadError('text', src.name, e.strerror)

def json(src):
    src = PosixPath(src)
    try:
        with src.open() as f:
            data = json_load(f)
            if type(data) == dict: data = NamedDict(src.name, data)
            return data
    except JSONDecodeError as e:
        raise LoadError('json', src.name, str(e))
    except IOError as e:
        raise LoadError('json', src.name, e.strerror)

def yaml(src):
    src = PosixPath(src)
    try:
        with src.open() as f:
            data = yaml_load(f)
            if type(data) == dict: data = NamedDict(src.name, data)
            return data
    except YAMLError as e:
        msg = e.problem
        if hasattr(e, 'problem_mark'):
            mark = e.problem_mark
            msg += f": line {mark.line + 1} column {mark.column + 1}"
        raise LoadError('yaml', src.name, msg)
    except IOError as e:
        raise LoadError('json', src.name, e.strerror)

def jinja(src, **kwargs):
    src = PosixPath(src)
    try:
        tmpl = src.read_text()
        return JINJA_ENV.from_string(tmpl).render(kwargs)
    except jinja2.TemplateError as e:
        msg = e.message
        if hasattr(e, 'lineno'): msg += f": line {e.lineno}"
        raise LoadError('jinja', src.name, msg)
    except IOError as e:
        raise LoadError('jinja', src.name, e.strerror)

def render(config):
    name = config.name if isinstance(config, NamedDict) else 'object'
    config = expand(config)
    res = subprocess.run(
        ['butane', '--files-dir', '.', *sys.argv[1:]],
        input=yaml_dump({**BUTANE_DEFAULTS, **config}),
        capture_output=True, text=True
    )
    if res.returncode == 0: return res.stdout
    else: raise RenderError(name, res.stderr.strip())

class NamedDict(dict):
    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
