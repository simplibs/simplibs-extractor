import pytest
from simplibs.exception import ParamError, SimpleError
from simplibs.exception.testing import assert_exception_function
from simplibs.extractor.logic.report._validations import raise_chars_per_token_error


@pytest.mark.parametrize("value", [0, 0.0, -1, -0.5], ids=["zero", "zero-float", "negative", "negative-float"])
def test_raise_chars_per_token_error_contract(subtests, value) -> None:
    """Verify raise_chars_per_token_error produces a well-formed ParamError card."""

    exc = assert_exception_function(
        subtests,
        raise_chars_per_token_error,
        invalid_params=(value,),
        exception_type=ParamError,
        error_name="EXTRACTOR_CONFIG_INVALID",
        label="parameter 'chars_per_token'",
        value=value,
        problem="The number of characters per token must be positive.",
        expected="A number greater than zero (about 4 for English text and code).",
        how_to_fix="Pass a positive number, or leave the default.",
        exception=ValueError,
        verbose=False,
    )

    # Catchable as the wrapped standard type and as "any error of this library"
    assert isinstance(exc, ValueError)
    assert isinstance(exc, SimpleError)
