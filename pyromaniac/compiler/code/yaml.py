from typing import Self, Any
from pathlib import PosixPath as Path
from json import JSONEncoder, dumps
from yaml import safe_load as yaml_load, MarkedYAMLError
from jinja2.exceptions import TemplateSyntaxError
from jinja2 import Environment, Template

from ..errors import CompilerError
from .errors import YamlTemplateError, YamlExecutionError, YamlParseError
from ..url import URL


def finalize(obj: Any) -> str:
    match obj:
        case Raw(content): return str(content)
        case _: return dumps(obj, cls=Encoder)


class Yaml:
    """Component YAML code."""

    environment = Environment(finalize=finalize)
    environment.filters['raw'] = lambda c: Raw(c)

    def __init__(self, template: Template):
        self.template = template

    @classmethod
    def create(cls, code: str) -> Self:
        """Create component yaml code.

        Creates a Jinja template from the code that is applied before parsing
        the yaml when executed.

        :param code: component yaml source code
        :returns: constructed component yaml code object
        """
        try:
            template = cls.environment.from_string(code)
        except TemplateSyntaxError as e:
            raise YamlTemplateError() from e

        return cls(template)

    def execute(self, context: dict) -> Any:
        """Execute component yaml code in given context.

        All fields from the context will be avaiable to the Jinja template.

        :param context: context to execute Jinja template in
        :returns: template execution result parsed as yaml source
        """
        try:
            yaml = self.template.render(context)
        except CompilerError as e:
            raise e
        except Exception as e:
            raise YamlExecutionError() from e

        try:
            return yaml_load(yaml)
        except MarkedYAMLError as e:
            raise YamlParseError() from e


class Raw:
    __match_args__ = ("content",)

    def __init__(self, content: Any):
        self.content = content


class Encoder(JSONEncoder):
    def default(self, obj: Any) -> Any:
        match obj:
            case Path() | URL(): return str(obj)
            case _: return super().default(obj)
