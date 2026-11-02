from simplibs.extractor.constants import LANGUAGE_BY_SUFFIX
from simplibs.extractor.registry._helpers import LANGUAGE_REGISTRY


def test_is_a_plain_dictionary() -> None:
    assert type(LANGUAGE_REGISTRY) is dict


def test_starts_with_every_built_in_language() -> None:
    assert LANGUAGE_BY_SUFFIX.items() <= LANGUAGE_REGISTRY.items()


def test_is_not_the_constant_itself() -> None:
    """A copy: registering a language must never change the read-only table."""
    assert LANGUAGE_REGISTRY is not LANGUAGE_BY_SUFFIX


def test_changing_it_does_not_change_the_constant() -> None:
    LANGUAGE_REGISTRY[".test-only"] = "x"
    try:
        assert ".test-only" not in LANGUAGE_BY_SUFFIX
    finally:
        del LANGUAGE_REGISTRY[".test-only"]


def test_every_key_is_a_lowercase_suffix_and_every_value_a_name() -> None:
    for suffix, language in LANGUAGE_REGISTRY.items():
        assert suffix.startswith(".") and len(suffix) > 1 and suffix == suffix.lower()
        assert language and not any(char.isspace() or char == "`" for char in language)
