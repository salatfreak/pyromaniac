from textwrap import dedent
import json
from yaml import safe_load as yaml_load, MarkedYAMLError

from jinja2 import TemplateSyntaxError
from jinja2.nodes import Expr, Pair, Dict, Const, CallBlock, Node
from jinja2.parser import Parser
from jinja2.ext import Extension
from jinja2.runtime import Macro

from ..expand import expand
from .errors import YamlParseError, YamlTemplateError
from .json import JSONEncoder


class RunExtension(Extension):
    """Extension for running functions and components."""
    tags = {'run'}

    def parse(self, parser: Parser) -> Node:
        lineno = next(parser.stream).lineno

        # parse function expression
        func = parser.parse_expression()

        # parse extra arguments
        strm, first = parser.stream, True
        args: list[Expr] = []
        kwargs: list[Pair] = []
        while not strm.current.test('block_end'):
            # expect comma unless first argument
            if first:
                first = False
            else:
                strm.expect('comma')

            # parse as keyword or positional arg
            if strm.current.type == 'name' and strm.look().type == 'assign':
                name = strm.expect('name').value
                strm.expect('assign')
                value = parser.parse_expression()
                kwargs.append(Pair(Const(name), value))
            else:
                args.append(parser.parse_expression())

        # parse body
        body = parser.parse_statements(('name:endrun',), drop_needle=True)

        # return instructions to call self._call_func
        call = self.call_method('_call_func', [
            func, Const(lineno), Dict(kwargs), *args,
        ])
        return CallBlock(call, [], [], body).set_lineno(lineno)

    def _call_func(self, func, lineno: int, kwargs, *args, caller: Macro):
        # parse YAML block
        block = dedent(caller().strip("\n"))
        try:
            content = expand(yaml_load(block))
        except MarkedYAMLError as e:
            e.context_mark
            raise YamlParseError() from e

        # assemble final args and kwargs
        match content:
            case list():
                args, kwargs = [*args, *content], kwargs
            case dict():
                args, kwargs = args, {**kwargs, **content}
            case _:
                raise YamlTemplateError from TemplateSyntaxError(
                    "Expected a list or dict inside Jinja {% run [...] %} "
                    "body", lineno
                )

        # call function and return serialized result
        return json.dumps(func(*args, **kwargs), cls=JSONEncoder)
