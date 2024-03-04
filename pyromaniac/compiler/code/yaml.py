from typing import Self, Any
from yaml import safe_load as yaml_load, MarkedYAMLError
from jinja2.exceptions import TemplateSyntaxError
from jinja2 import Template

from ..errors import CompilerError
from .errors import YamlTemplateError, YamlExecutionError, YamlParseError
from .jinja import json_env as environment


class Yaml:
    """Component YAML code."""

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
            template = environment.from_string(code)
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
