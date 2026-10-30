import pytest
from simplibs.exception import ParamError, SimpleError
from simplibs.exception.testing import assert_exception_function
from simplibs.extractor.definitions._validations import raise_profile_output_name_error


@pytest.mark.parametrize("value", ["x/y.md", "", "a\\b.md", None], ids=["slash", "empty", "backslash", "none"])
def test_raise_profile_output_name_error_contract(subtests, value) -> None:
    """Verify raise_profile_output_name_error produces a well-formed ParamError card."""

    expected = "a portable file name (no path separators or forbidden characters)"

    exc = assert_exception_function(
        subtests,
        raise_profile_output_name_error,
        invalid_params=(value,),
        exception_type=ParamError,
        error_name="EXTRACTOR_PROFILE_INVALID",
        label="profile output_name",
        value=value,
        problem=f"The output name {value!r} is not a usable file name.",
        expected=expected,
        how_to_fix=f"Provide {expected}.",
        exception=ValueError,
        verbose=False,
    )

    # Catchable as the wrapped standard type and as "any error of this library"
    assert isinstance(exc, ValueError)
    assert isinstance(exc, SimpleError)
