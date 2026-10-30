import pytest
from simplibs.exception import ParamError, SimpleError
from simplibs.exception.testing import assert_exception_function
from simplibs.extractor.registry._validations import raise_renderer_exists_error


@pytest.mark.parametrize("name", ["markdown", "plain", "my-format"], ids=["markdown", "plain", "custom"])
def test_raise_renderer_exists_error_contract(subtests, name) -> None:
    """Verify raise_renderer_exists_error produces a well-formed ParamError card that names the taken format."""

    exc = assert_exception_function(
        subtests,
        raise_renderer_exists_error,
        invalid_params=(name,),
        exception_type=ParamError,
        error_name="EXTRACTOR_CONFIG_INVALID",
        label=f"renderer '{name}'",
        value=name,
        problem=f"A renderer is already registered for the format '{name}'.",
        expected="A format name that is not registered yet, or replace_existing=True.",
        how_to_fix="Pass replace_existing=True, or choose a different format name.",
        exception=ValueError,
        verbose=False,
    )

    # Catchable as the wrapped standard type and as "any error of this library"
    assert isinstance(exc, ValueError)
    assert isinstance(exc, SimpleError)
