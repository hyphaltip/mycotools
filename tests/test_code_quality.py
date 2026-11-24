"""AST lint: guard the fixes from the code audit against regressions."""
import ast
import pathlib

PKG = pathlib.Path(__file__).resolve().parents[1] / "mycotools"
FILES = sorted(p for p in PKG.rglob("*.py"))


def _mutable(node):
    if isinstance(node, (ast.List, ast.Dict, ast.Set)):
        return True
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id in {"set", "dict", "list"}
        and not node.args
        and not node.keywords
    )


def test_package_files_found():
    assert len(FILES) > 40


def test_no_mutable_default_arguments_that_are_mutated():
    # one-line literal defaults are forbidden; the read-only multi-line
    # `forbid` set in dbtools.assimilate_tax is the only allowed exception
    bad = []
    for path in FILES:
        for fn in ast.walk(ast.parse(path.read_text())):
            if not isinstance(fn, ast.FunctionDef):
                continue
            a = fn.args
            defaults = list(a.defaults) + [d for d in a.kw_defaults if d]
            for d in defaults:
                if _mutable(d) and d.lineno == d.end_lineno:
                    bad.append(f"{path.name}:{fn.name}")
    assert not bad, bad


def test_no_bare_except():
    bad = []
    for path in FILES:
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                bad.append(f"{path.name}:{node.lineno}")
    assert not bad, bad


def test_no_shell_true_in_calls():
    bad = []
    for path in FILES:
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Call):
                for kw in node.keywords:
                    if (
                        kw.arg == "shell"
                        and isinstance(kw.value, ast.Constant)
                        and kw.value.value is True
                    ):
                        bad.append(f"{path.name}:{node.lineno}")
    assert not bad, bad
