import ast
import pytest
from simplibs.extractor.constants import SCRIPT_TEMPLATE


def _render(profile: str) -> str:
    return SCRIPT_TEMPLATE.format(file_name="extract_here.py", profile=profile)


def _profile_argument(source: str) -> str:
    """Read the value of `profile=` back out of the generated call, the way Python itself reads it."""
    call = next(
        node
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "extract_here"
    )
    return {keyword.arg: ast.literal_eval(keyword.value) for keyword in call.keywords}["profile"]


def test_value() -> None:
    """The script template contains the expected structure and placeholder keys."""
    assert isinstance(SCRIPT_TEMPLATE, str)
    assert "#!/usr/bin/env python3" in SCRIPT_TEMPLATE
    assert "extract_here" in SCRIPT_TEMPLATE
    assert "{file_name}" in SCRIPT_TEMPLATE
    assert "{profile!r}" in SCRIPT_TEMPLATE


def test_template_has_exactly_two_placeholders() -> None:
    """Filling in `file_name` and `profile` leaves no stray braces (any other one would make `format` fail)."""
    text = _render("generic/all")
    assert "{" not in text and "}" not in text
    assert "python extract_here.py" in text


def test_filled_template_is_valid_python() -> None:
    """The generated script compiles."""
    compile(_render("generic/all"), "extract_here.py", "exec")


def test_script_runs_only_as_a_main_script() -> None:
    """Importing the generated script must not start an extraction."""
    assert 'if __name__ == "__main__":' in SCRIPT_TEMPLATE


@pytest.mark.parametrize(
    "profile",
    [
        "generic/all",
        "python/code-clean",
        "a'b",
        'a"b',
        "a'b\"c",
        "back\\slash",
        "ž/č",
        "{braces}",
        "line\nbreak",
    ],
)
def test_profile_survives_the_round_trip(profile) -> None:
    """Whatever the profile text is, the generated script compiles and passes exactly that text on."""
    source = _render(profile)
    compile(source, "extract_here.py", "exec")
    assert _profile_argument(source) == profile
