import pytest
from simplibs.exception import ParamError, ValidationError
from simplibs.exception.testing import assert_exception_function
from simplibs.extractor.registry import get_language, list_languages, register_language
from simplibs.extractor.registry._helpers import LANGUAGE_REGISTRY


@pytest.fixture(autouse=True)
def _restore_languages():
    """A registered language must not leak into the next test."""
    saved = dict(LANGUAGE_REGISTRY)
    yield
    LANGUAGE_REGISTRY.clear()
    LANGUAGE_REGISTRY.update(saved)


def test_registers_a_language_under_its_suffix() -> None:
    register_language(".lua", "lua")
    assert LANGUAGE_REGISTRY[".lua"] == "lua"
    assert get_language(".lua") == "lua"
    assert ".lua" in list_languages()


def test_returns_none() -> None:
    assert register_language(".lua", "lua") is None


@pytest.mark.parametrize("language", ["lua", "c++", "objective-c", "C#", "js_x"])
def test_accepts_the_usual_language_names(language) -> None:
    register_language(".zzz", language)
    assert get_language(".zzz") == language


def test_taken_suffix_gives_a_config_invalid_card(subtests) -> None:
    """A second language for a taken suffix is refused (the built-in suffixes are taken from the start)."""
    assert_exception_function(
        subtests,
        lambda suffix: register_language(suffix, "x"),
        invalid_params=(".py",),
        valid_params=(".fresh",),
        exception_type=ParamError,
        error_name="EXTRACTOR_CONFIG_INVALID",
        label="language of '.py'",
        value=".py",
        problem="A language is already registered for the suffix '.py'.",
        expected="A suffix that has no language yet, or replace_existing=True.",
        how_to_fix="Pass replace_existing=True, or choose a different suffix.",
        verbose=False,
    )


def test_refused_registration_keeps_the_original() -> None:
    with pytest.raises(ParamError):
        register_language(".py", "snake")
    assert get_language(".py") == "python"


def test_replace_existing_replaces() -> None:
    register_language(".lua", "lua")
    register_language(".lua", "luau", replace_existing=True)
    assert get_language(".lua") == "luau"


def test_a_built_in_suffix_can_be_replaced_on_request() -> None:
    register_language(".py", "python3", replace_existing=True)
    assert get_language(".py") == "python3"


@pytest.mark.parametrize("suffix", ["lua", ".LUA", ".", "", ". x", " .lua", ".l ua", "*"])
def test_suffix_must_be_lowercase_with_a_dot_and_something_after_it(suffix) -> None:
    with pytest.raises(ParamError):
        register_language(suffix, "lua")
    assert suffix not in LANGUAGE_REGISTRY


@pytest.mark.parametrize("language", ["", " ", "a b", "a\tb", "a`b", "```"])
def test_language_must_be_writable_after_a_fence(language) -> None:
    with pytest.raises(ParamError):
        register_language(".zzz", language)
    assert ".zzz" not in LANGUAGE_REGISTRY


def test_the_suffix_card_names_the_parameter(subtests) -> None:
    assert_exception_function(
        subtests,
        lambda suffix: register_language(suffix, "lua"),
        invalid_params=("lua",),
        valid_params=(".lua",),
        exception_type=ParamError,
        error_name="EXTRACTOR_CONFIG_INVALID",
        label="parameter 'suffix'",
        value="lua",
        problem="'lua' is not a usable file suffix.",
        verbose=False,
    )


def test_the_language_card_names_the_parameter(subtests) -> None:
    assert_exception_function(
        subtests,
        lambda language: register_language(".zzz", language),
        invalid_params=("a b",),
        valid_params=("lua",),
        exception_type=ParamError,
        error_name="EXTRACTOR_CONFIG_INVALID",
        label="parameter 'language'",
        value="a b",
        problem="'a b' cannot be written after a code fence.",
        verbose=False,
    )


@pytest.mark.parametrize("suffix, language", [(None, "lua"), (5, "lua"), (".lua", None), (".lua", 5), (["a"], "lua")])
def test_both_must_be_texts(suffix, language) -> None:
    with pytest.raises(ValidationError):
        register_language(suffix, language)


def test_replace_existing_is_keyword_only() -> None:
    with pytest.raises(TypeError):
        register_language(".lua", "lua", True)  # type: ignore[misc]
