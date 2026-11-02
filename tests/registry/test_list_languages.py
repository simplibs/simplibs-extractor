import pytest
from simplibs.exception import ValidationError
from simplibs.extractor.constants import LANGUAGE_BY_SUFFIX
from simplibs.extractor.registry import get_language, list_languages, register_language
from simplibs.extractor.registry._helpers import LANGUAGE_REGISTRY


@pytest.fixture(autouse=True)
def _restore_languages():
    saved = dict(LANGUAGE_REGISTRY)
    yield
    LANGUAGE_REGISTRY.clear()
    LANGUAGE_REGISTRY.update(saved)


def test_lists_the_built_in_languages() -> None:
    languages = list_languages()
    for suffix, language in LANGUAGE_BY_SUFFIX.items():
        assert languages[suffix] == language


def test_is_sorted_by_suffix() -> None:
    keys = list(list_languages())
    assert keys == sorted(keys)


def test_includes_a_registered_language_in_its_place() -> None:
    register_language(".a-first", "x")
    assert list(list_languages())[0] == ".a-first"
    assert list_languages()[".a-first"] == "x"


def test_is_a_copy_that_cannot_change_the_registry() -> None:
    languages = list_languages()
    languages.clear()
    languages[".evil"] = "evil"
    assert get_language(".py") == "python"
    assert ".evil" not in LANGUAGE_REGISTRY
    assert list_languages() is not list_languages()


def test_takes_no_arguments() -> None:
    with pytest.raises((TypeError, ValidationError)):
        list_languages(".py")  # type: ignore[call-arg]
