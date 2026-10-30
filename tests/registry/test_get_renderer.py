import pytest
from simplibs.exception import ParamError, ValidationError
from simplibs.exception.testing import assert_exception_function
from simplibs.extractor.registry import get_renderer, register_renderer
from simplibs.extractor.registry._helpers import RENDERER_REGISTRY


def fake_renderer(entries, context) -> str:
    return "rendered"


@pytest.mark.parametrize("name", ["markdown", "plain"])
def test_built_in_formats_are_available(name) -> None:
    assert callable(get_renderer(name))


def test_returns_the_registered_function() -> None:
    register_renderer("custom", fake_renderer)
    assert get_renderer("custom") is fake_renderer


def test_unknown_format_gives_a_config_invalid_card_listing_the_formats(subtests) -> None:
    """The card names what exists, sorted."""
    RENDERER_REGISTRY.clear()
    register_renderer("zeta", fake_renderer)
    register_renderer("alpha", fake_renderer)
    assert_exception_function(
        subtests,
        get_renderer,
        invalid_params=("pdf",),
        valid_params=("alpha",),
        exception_type=ParamError,
        error_name="EXTRACTOR_CONFIG_INVALID",
        label="parameter 'format'",
        value="pdf",
        problem="No renderer is registered for the format 'pdf'.",
        expected="One of the registered formats: alpha, zeta.",
        how_to_fix="Choose a registered format, or add one with register_renderer().",
        verbose=False,
    )


def test_empty_registry_says_so(subtests) -> None:
    RENDERER_REGISTRY.clear()
    assert_exception_function(
        subtests,
        get_renderer,
        invalid_params=("markdown",),
        exception_type=ParamError,
        error_name="EXTRACTOR_CONFIG_INVALID",
        expected="One of the registered formats: (none registered).",
        verbose=False,
    )


@pytest.mark.parametrize("name", ["Markdown", " markdown", "markdown ", ""])
def test_the_name_must_match_exactly(name) -> None:
    with pytest.raises(ParamError):
        get_renderer(name)


@pytest.mark.parametrize("name", [None, 5, b"markdown", ["markdown"]])
def test_the_name_must_be_text(name) -> None:
    with pytest.raises(ValidationError):
        get_renderer(name)
