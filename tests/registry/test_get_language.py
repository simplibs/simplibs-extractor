import pytest
from simplibs.exception import ValidationError
from simplibs.extractor.registry import get_language, register_language
from simplibs.extractor.registry._helpers import LANGUAGE_REGISTRY


@pytest.fixture(autouse=True)
def _restore_languages():
    saved = dict(LANGUAGE_REGISTRY)
    yield
    LANGUAGE_REGISTRY.clear()
    LANGUAGE_REGISTRY.update(saved)


@pytest.mark.parametrize(
    "suffix, language",
    [(".py", "python"), (".js", "javascript"), (".mjs", "javascript"), (".cjs", "javascript"), (".md", "markdown")],
)
def test_built_in_suffixes_have_their_language(suffix, language) -> None:
    assert get_language(suffix) == language


@pytest.mark.parametrize("suffix", [".PY", ".Py", ".MJS"])
def test_the_case_of_the_suffix_is_ignored(suffix) -> None:
    assert get_language(suffix) == get_language(suffix.lower())
    assert get_language(suffix) is not None


@pytest.mark.parametrize("suffix", [".lua", ".nothing", "", "py", "."])
def test_an_unknown_suffix_has_no_language(suffix) -> None:
    """Not knowing is an answer, not an error."""
    assert get_language(suffix) is None


def test_a_registered_language_is_found() -> None:
    register_language(".lua", "lua")
    assert get_language(".lua") == "lua"


@pytest.mark.parametrize("suffix", [None, 5, [".py"], b".py"])
def test_the_suffix_must_be_a_text(suffix) -> None:
    with pytest.raises(ValidationError):
        get_language(suffix)
