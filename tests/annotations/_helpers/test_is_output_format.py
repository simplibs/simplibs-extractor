import pytest
from simplibs.extractor.annotations._helpers import is_output_format


@pytest.mark.parametrize(
    "value",
    ["markdown", "plain", "json-manifest", "html5", "txt", "a-b-c", "format1", "a", "snake_case"],
)
def test_is_output_format_accepts_valid_names(value) -> None:
    """A valid format name starts with a letter and contains only lowercase letters, digits, underscores, and hyphens."""
    assert is_output_format(value) is True


@pytest.mark.parametrize(
    "value",
    [
        "Markdown",        # uppercase letters are rejected
        "markdown format", # spaces are rejected
        "-format",         # starting with a hyphen is rejected
        "_format",         # starting with an underscore is rejected
        "1format",         # starting with a digit is rejected
        "format.name",     # dots/path separators are rejected
        "markdown\n",      # a trailing newline must not slip through
        "markdown ",       # trailing space
        " markdown",       # leading space
        "markdown\t",      # trailing tab
        "příliš",          # accented letters are not [a-z]
        "",                # empty string is rejected
        None,
        42,
        b"markdown",
        ["markdown"],
    ],
)
def test_is_output_format_rejects_invalid_names(value) -> None:
    """Invalid shapes, non-lowercase names, and non-strings are rejected without raising."""
    assert is_output_format(value) is False
