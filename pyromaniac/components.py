import os
import ast
from pathlib import PosixPath, Path
from yaml import add_representer

from .utils import NamedDict
from . import utils as u
from .errors import PyromaniacError, LoadError, ComponentError

# Allow paths in 
add_representer(PosixPath, lambda d, s: d.represent_scalar('!!str', str(s)))

def load(root):
    root = PosixPath(root)
    comps = ComponentDict()
    for path in root.glob('**/*.py'):
        comp = Component.from_path(root, path, comps)
        comps.insert(comp.place, comp)
    return comps

def modify_code(name, code):
    tree = ast.parse(code, name)
    last = tree.body[-1]
    if not isinstance(last, ast.Expr):
        raise ComponentError(name, "doesn't end with expression")
    tree.body[-1] = ast.Assign(
        targets=[ast.Name(id='result', ctx=ast.Store())],
        value=tree.body[-1].value,
        lineno=tree.body[-1].lineno,
    )
    return ast.unparse(tree)

class Component:
    def __init__(self, path, place, comps):
        self.path = PosixPath(path)
        self.place = place
        self.comps = comps
        self.code = None

    @classmethod
    def from_path(cls, root, path, comps):
        place = [*path.relative_to(root).parent.parts, path.stem]
        return cls(path, place, comps)

    def __call__(self, *args, **kwargs):
        context = {
            **CONTEXT, **self.comps,
            '_': Underscore(self.path.parent, self.local_comps()),
            'args': args, 'kwargs': kwargs
        }
        self.ensure_loaded()
        try: exec(self.code, context)
        except PyromaniacError as e: raise e
        except Exception as e: raise ComponentError(self.path.name, str(e))
        result = context['result']
        if type(result) == dict: result = NamedDict(self.path.name, result)
        return result

    def local_comps(self):
        comps = self.comps
        for part in self.place[:-1]:
            comps = comps[part]
        return comps
    
    def ensure_loaded(self):
        if self.code is not None: return
        name = self.path.name
        try:
            self.code = modify_code(name, self.path.read_text())
        except SyntaxError as e:
            raise ComponentError(name, f"{e.msg}: line {e.lineno}")
        except IOError as e:
            raise LoadError('component', name, e.strerror)

class Underscore:
    def __init__(self, path, comps):
        self._path = path
        self._comps = comps

    def __getattr__(self, key):
        return self._comps[key]
    
    def __truediv__(self, path):
        return self._path / path

class ComponentDict(dict):
    __getattr__ = dict.__getitem__

    def __call__(self, *args, **kwargs):
        return self['main'](*args, **kwargs)

    def insert(self, place, item):
        if len(place) == 1:
            self[place[0]] = item
        else:
            if not place[0] in self: self[place[0]] = ComponentDict()
            self[place[0]].insert(place[1:], item)

CONTEXT = {
    **{ f.__name__: f for f in [u.load, u.json, u.yaml, u.jinja, u.render] },
    **load(PosixPath(__file__).parent / 'components'),
    'env': os.environ, 'Path': Path,
}
