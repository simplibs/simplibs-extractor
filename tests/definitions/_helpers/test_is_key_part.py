import pytest
from simplibs.extractor.definitions._helpers import is_key_part


@pytest.mark.parametrize(
    "value",
    ["python", "code-clean", "generic", "a", "a.b", "a_b", "python3", "česky", "*", "ALL"],
)
def test_is_key_part_accepts_usable_parts(value) -> None:
    """A part is a non-blank text without '/', ',' or whitespace."""
    assert is_key_part(value) is True


@pytest.mark.parametrize(
    "value",
    [
        "",           # empty
        " ",          # blank
        "a b",        # inner space
        " a",         # leading space
        "a ",         # trailing space
        "a/b",        # the key separator
        "a,b",        # the CLI list separator
        "/",
        ",",
        "a\tb",       # tab
        "a\nb",       # newline
        "a\u00a0b",   # non-breaking space is whitespace too
    ],
)
def test_is_key_part_rejects_unusable_text(value) -> None:
    """Blank, padded, or separator-bearing text is rejected."""
    assert is_key_part(value) is False


@pytest.mark.parametrize("value", [None, 5, 1.5, b"python", ["python"], ("a",), object()])
def test_is_key_part_rejects_non_strings_without_raising(value) -> None:
    """Anything that is not a string is a plain False."""
    assert is_key_part(value) is False
