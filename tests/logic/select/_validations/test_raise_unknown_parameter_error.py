import pytest
from simplibs.exception import ParamError, SimpleError
from simplibs.exception.testing import assert_exception_function
from simplibs.extractor.logic.select._validations import raise_unknown_parameter_error


@pytest.mark.parametrize(
    "unknown, known",
    [
        (["sourse"], ["source", "target"]),
        (["a", "b"], ["source"]),
        (["x"], []),
    ],
    ids=["one-unknown", "several-unknown", "no-known"],
)
def test_raise_unknown_parameter_error_contract(subtests, unknown, known) -> None:
    """Verify raise_unknown_parameter_error produces a well-formed ParamError card that lists both sides."""

    exc = assert_exception_function(
        subtests,
        raise_unknown_parameter_error,
        invalid_params=(unknown, known),
        exception_type=ParamError,
        error_name="EXTRACTOR_CONFIG_INVALID",
        label="extraction parameters",
        value=unknown,
        problem=f"Unknown parameter(s): {', '.join(unknown)}.",
        expected=f"Only these parameters: {', '.join(known)}.",
        how_to_fix="Check the spelling of the parameter names.",
        exception=ValueError,
        verbose=False,
    )

    # Catchable as the wrapped standard type and as "any error of this library"
    assert isinstance(exc, ValueError)
    assert isinstance(exc, SimpleError)
