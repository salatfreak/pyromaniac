from unittest import TestCase
from textwrap import dedent

from pyromaniac.compiler.code.errors import YamlTemplateError, YamlParseError
from pyromaniac.compiler.code.yaml import Yaml


def execute(code: str, context: dict | None = None) -> dict:
    return Yaml.create(code).execute(context or {})


ctx = {'sum': lambda a, b, c: a + b + c}


class RunExtentionTest(TestCase):
    def test_list(self):
        self.assertEqual(30.14, execute(dedent("""
            {% run sum %}
              - -42
              - 69
              - 3.14
            {% endrun %}
        """.strip()), ctx))

    def test_dict(self):
        self.assertEqual(30.14, execute(dedent("""
            {% run sum %}
              a: -42
              b: 69
              c: 3.14
            {% endrun %}
        """.strip()), ctx))

    def test_mixed(self):
        self.assertEqual(30.14, execute(dedent("""
            {%run sum c = 3.14, -42%}
              b: 69
            {%endrun%}
        """.strip()), ctx))

    def test_nested(self):
        self.assertEqual(49, execute(dedent("""
            {% run sum 1 %}
              - 42
              - {% run sum 1, 2 %}
                c: 3
              {% endrun %}
            {% endrun %}
        """.strip()), ctx))

    def test_trailing_comma(self):
        with self.assertRaises(YamlTemplateError):
            execute(dedent("""
              {% run sum c = 3.14, -42, %}
                b: 69
              {% endrun %}
            """.strip()), ctx)

    def test_invalid_type(self):
        with self.assertRaises(YamlTemplateError):
            execute(dedent("""
                {%  run sum %}
                  42
                {% endrun %}
            """.strip()), ctx)

    def test_invalid_yaml(self):
        with self.assertRaises(YamlParseError):
            execute(dedent("""
                {% run sum %}
                  a: b: c
                {% endrun %}
            """.strip()), ctx)
