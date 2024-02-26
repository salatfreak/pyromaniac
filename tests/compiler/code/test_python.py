from unittest import TestCase
from pyromaniac.compiler.code.errors import (
    PythonSyntaxError, PythonRuntimeError
)
from pyromaniac.compiler.code.python import Python


def execute(
    code: str, context: dict | None = None, pure: bool = False,
) -> dict:
    context = context or {}
    Python.create(code, pure).execute(context)
    return context


class TestPython(TestCase):
    def test_empty(self):
        self.assertEqual(execute(""), {})

    def test_function(self):
        code = "def foo(): return 42\nnum = foo()"
        self.assertEqual(execute(code)["num"], 42)

    def test_pure(self):
        ctx = {"a": 42, "b": 69}
        self.assertEqual(execute("a + b", ctx, True)["result"], 42 + 69)

    def test_syntax_error(self):
        self.assertRaisesPythonSyntax("if for: true")

    def test_invalid_pure(self):
        self.assertRaisesPythonSyntax("", True)
        self.assertRaisesPythonSyntax("if True: 'hello'", True)
        self.assertRaisesPythonSyntax("num = 42", True)

    def test_runtime_error(self):
        self.assertRaisesPythonRuntime("42 + '69'")
        self.assertRaisesPythonRuntime("raise ValueError()")

    def test_error_pass_through(self):
        rte = PythonRuntimeError()
        raised = self.assertRaisesPythonRuntime("raise e", {"e": rte})
        self.assertIs(rte, raised)

    def assertRaisesPythonSyntax(self, code: str, pure: bool = False):
        with self.assertRaises(PythonSyntaxError):
            Python.create(code, pure)

    def assertRaisesPythonRuntime(
        self, code: str, context: dict = None, pure: bool = False,
    ) -> Exception:
        with self.assertRaises(PythonRuntimeError) as e:
            execute(code, context, pure)
        return e.exception
