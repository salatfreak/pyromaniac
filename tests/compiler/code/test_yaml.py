from unittest import TestCase
from pathlib import PosixPath as Path
from pyromaniac.compiler.url import URL
from pyromaniac.compiler.code.errors import (
    YamlTemplateError, YamlExecutionError, YamlParseError,
)
from pyromaniac.compiler.code.yaml import Yaml


def execute(code: str, context: dict | None = None) -> dict:
    return Yaml.create(code).execute(context or {})


class TestYaml(TestCase):
    def test_empty(self):
        self.assertIsNone(execute(""), None)

    def test_insert_variable(self):
        self.assertEqual(execute("foo-`var`", {"var": "bar"}), 'foo-"bar"')
        self.assertEqual(
            execute("r: `a + b`", {"a": 42, "b": 69}),
            {"r": 42 + 69},
        )

    def test_raw_filter(self):
        self.assertEqual(
            execute("foo-`var | raw`", {"var": "bar"}),
            "foo-bar",
        )

    def test_structured_data(self):
        self.assertEqual(
            execute("foo: 69\nbar: `bar`", {"bar": [42, 3.1415]}),
            {"foo": 69, "bar": [42, 3.1415]},
        )

    def test_path_and_url(self):
        ctx = {"path": Path("/foo/bar"), "url": URL("https://example.com/")}
        self.assertEqual(
            execute("foo: `path`\nbar: `url`", ctx),
            {"foo": "/foo/bar", "bar": "https://example.com/"},
        )

    def test_template_error(self):
        self.assertRaisesYamlTemplate("foo: `")
        self.assertRaisesYamlTemplate("`||`")
        self.assertRaisesYamlTemplate("`if then what`")

    def test_execution_error(self):
        err = ValueError()

        def f():
            raise err
        raised = self.assertRaisesYamlExecution("`f()`", {"f": f})
        self.assertIs(raised.__cause__, err)

        raised = self.assertRaisesYamlExecution("`'foo' + 42`")
        self.assertIsInstance(raised.__cause__, TypeError)

    def test_parse_error(self):
        self.assertRaisesYamlParse("foo: bar: `'baz'`")
        self.assertRaisesYamlParse("qux: '")

    def assertRaisesYamlTemplate(self, code: str):
        with self.assertRaises(YamlTemplateError):
            Yaml.create(code)

    def assertRaisesYamlExecution(
        self, code: str, context: dict = None,
    ) -> Exception:
        with self.assertRaises(YamlExecutionError) as e:
            execute(code, context)
        return e.exception

    def assertRaisesYamlParse(
        self, code: str, context: dict = None,
    ) -> Exception:
        with self.assertRaises(YamlParseError) as e:
            execute(code, context)
        return e.exception
