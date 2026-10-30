import pytest
from simplibs.exception import ParamError, SimpleError
from simplibs.exception.testing import assert_exception_function
from simplibs.extractor.registry._helpers import RENDERER_REGISTRY
from simplibs.extractor.registry._validations import raise_unknown_renderer_error


@pytest.mark.parametrize("name", ["html", "", "MARKDOWN"], ids=["unknown", "empty", "wrong-case"])
def test_raise_unknown_renderer_error_contract(subtests, name) -> None:
    """Verify raise_unknown_renderer_error produces a well-formed ParamError card listing the registered formats."""

    listed = ", ".join(sorted(RENDERER_REGISTRY)) or "(none registered)"

    exc = assert_exception_function(
        subtests,
        raise_unknown_renderer_error,
        invalid_params=(name,),
        exception_type=ParamError,
        error_name="EXTRACTOR_CONFIG_INVALID",
        label="parameter 'format'",
        value=name,
        problem=f"No renderer is registered for the format {name!r}.",
        expected=f"One of the registered formats: {listed}.",
        how_to_fix="Choose a registered format, or add one with register_renderer().",
        exception=ValueError,
        verbose=False,
    )

    # Catchable as the wrapped standard type and as "any error of this library"
    assert isinstance(exc, ValueError)
    assert isinstance(exc, SimpleError)


def test_raise_unknown_renderer_error_with_empty_registry(subtests, monkeypatch) -> None:
    """Verify the card says '(none registered)' when no renderer exists at all."""

    for key in list(RENDERER_REGISTRY):
        monkeypatch.delitem(RENDERER_REGISTRY, key)

    assert_exception_function(
        subtests,
        raise_unknown_renderer_error,
        invalid_params=("html",),
        exception_type=ParamError,
        error_name="EXTRACTOR_CONFIG_INVALID",
        label="parameter 'format'",
        value="html",
        problem="No renderer is registered for the format 'html'.",
        expected="One of the registered formats: (none registered).",
        how_to_fix="Choose a registered format, or add one with register_renderer().",
        exception=ValueError,
        verbose=False,
    )
