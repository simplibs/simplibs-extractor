import ast
import pytest
from simplibs.extractor.constants import SCRIPT_TEMPLATE
from simplibs.extractor.scripts import render_script


def test_it_fills_in_the_template() -> None:
    assert render_script("extract_here.py", "generic/all") == SCRIPT_TEMPLATE.format(
        file_name="extract_here.py", profile="generic/all"
    )


def test_the_file_name_is_shown_in_the_run_line() -> None:
    assert "python my_script.py" in render_script("my_script.py", "generic/all")


def test_the_profile_key_is_written_as_a_python_string() -> None:
    assert "profile='python/code-clean'" in render_script("x.py", "python/code-clean")


def test_the_script_compiles() -> None:
    compile(render_script("x.py", "generic/all"), "x.py", "exec")


@pytest.mark.parametrize("key", ["a'b/c", 'a"b/c', "back\\slash/x", "ž/č", "{x}/{y}"])
def test_no_key_can_break_the_code(key) -> None:
    source = render_script("x.py", key)
    tree = ast.parse(source)
    call = next(node for node in ast.walk(tree) if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "extract_here")
    assert ast.literal_eval(call.keywords[0].value) == key


def test_the_script_uses_the_public_entry_point() -> None:
    assert "from simplibs.extractor import extract_here" in render_script("x.py", "generic/all")


def test_it_returns_text() -> None:
    assert isinstance(render_script("x.py", "generic/all"), str)
