import pytest
from simplibs.exception import ParamError, ValidationError
from simplibs.exception.testing import assert_exception_function
from simplibs.extractor.registry import get_renderer, list_formats, register_renderer
from simplibs.extractor.registry._helpers import RENDERER_REGISTRY


def fake_renderer(entries, context) -> str:
    return "rendered"


def other_renderer(entries, context) -> str:
    return "other"


def test_registers_a_renderer_under_its_name() -> None:
    register_renderer("custom", fake_renderer)
    assert RENDERER_REGISTRY["custom"] is fake_renderer
    assert get_renderer("custom") is fake_renderer
    assert "custom" in list_formats()


def test_returns_none() -> None:
    assert register_renderer("custom", fake_renderer) is None


@pytest.mark.parametrize("name", ["custom", "json-manifest", "html5", "snake_case"])
def test_accepts_every_valid_format_name(name) -> None:
    register_renderer(name, fake_renderer)
    assert get_renderer(name) is fake_renderer


def test_taken_name_gives_a_config_invalid_card(subtests) -> None:
    """A second renderer under a taken name is refused (the built-in names are taken from the start)."""
    assert_exception_function(
        subtests,
        lambda name: register_renderer(name, fake_renderer),
        invalid_params=("markdown",),
        valid_params=("fresh",),
        exception_type=ParamError,
        error_name="EXTRACTOR_CONFIG_INVALID",
        label="renderer 'markdown'",
        value="markdown",
        problem="A renderer is already registered for the format 'markdown'.",
        expected="A format name that is not registered yet, or replace_existing=True.",
        how_to_fix="Pass replace_existing=True, or choose a different format name.",
        verbose=False,
    )


def test_refused_registration_keeps_the_original() -> None:
    register_renderer("custom", fake_renderer)
    with pytest.raises(ParamError):
        register_renderer("custom", other_renderer)
    assert get_renderer("custom") is fake_renderer


def test_replace_existing_replaces() -> None:
    register_renderer("custom", fake_renderer)
    register_renderer("custom", other_renderer, replace_existing=True)
    assert get_renderer("custom") is other_renderer


def test_built_in_format_can_be_replaced_on_request() -> None:
    register_renderer("markdown", other_renderer, replace_existing=True)
    assert get_renderer("markdown") is other_renderer


@pytest.mark.parametrize("name", ["Custom", "two words", "", "-x", "1x", "a.b", None, 5])
def test_name_must_have_the_shape_of_a_format(name) -> None:
    with pytest.raises(ValidationError):
        register_renderer(name, fake_renderer)


@pytest.mark.parametrize("func", ["not callable", None, 5, ["x"]])
def test_renderer_must_be_callable(func) -> None:
    with pytest.raises(ValidationError):
        register_renderer("custom", func)


def test_replace_existing_is_keyword_only() -> None:
    with pytest.raises(TypeError):
        register_renderer("custom", fake_renderer, True)  # type: ignore[misc]
