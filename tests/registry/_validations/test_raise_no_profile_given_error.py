import pytest
from simplibs.exception import ParamError, SimpleError
from simplibs.exception.testing import assert_exception_function
from simplibs.extractor.registry._validations import raise_no_profile_given_error


@pytest.mark.parametrize("names", ["", " , ", [], ("", " ")], ids=["empty-text", "blank-commas", "empty-list", "blank-tuple"])
def test_raise_no_profile_given_error_contract(subtests, names) -> None:
    """Verify raise_no_profile_given_error produces a well-formed ParamError card; the value is what the caller passed."""

    expected = "at least one profile name"

    exc = assert_exception_function(
        subtests,
        raise_no_profile_given_error,
        invalid_params=(names,),
        exception_type=ParamError,
        error_name="EXTRACTOR_PROFILE_INVALID",
        label="profile keys",
        value=names,
        problem="No profile was given.",
        expected=expected,
        how_to_fix=f"Provide {expected}.",
        exception=ValueError,
        verbose=False,
    )

    # Catchable as the wrapped standard type and as "any error of this library"
    assert isinstance(exc, ValueError)
    assert isinstance(exc, SimpleError)
