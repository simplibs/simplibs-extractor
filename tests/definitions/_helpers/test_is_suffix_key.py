import pytest
from simplibs.extractor.definitions._helpers import is_suffix_key


@pytest.mark.parametrize("value", ["*", ".py", ".md", ".d", ".py3", ".gz", ".yaml"])
def test_is_suffix_key_accepts_fallback_and_lowercase_suffixes(value) -> None:
    """'*' (the fallback) and a lowercase dotted suffix are valid keys."""
    assert is_suffix_key(value) is True


@pytest.mark.parametrize(
    "value",
    [
        "",        # empty
        ".",       # a dot alone
        "py",      # missing dot
        ".PY",     # uppercase can never match (suffixes are lowercased before the lookup)
        ".Py",
        "**",
        "*.py",
        " .py",    # padded in front
    ],
)
def test_is_suffix_key_rejects_keys_that_can_never_match(value) -> None:
    """A key that no file suffix could ever equal is rejected."""
    assert is_suffix_key(value) is False


@pytest.mark.parametrize("value", [None, 5, b".py", [".py"], (".py",)])
def test_is_suffix_key_rejects_non_strings_without_raising(value) -> None:
    """Anything that is not a string is a plain False."""
    assert is_suffix_key(value) is False
