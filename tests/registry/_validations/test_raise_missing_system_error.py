import pytest
from simplibs.exception import ParamError, SimpleError
from simplibs.exception.testing import assert_exception_function
from simplibs.extractor.registry._validations import raise_missing_system_error


@pytest.mark.parametrize("name", ["code-clean", "x", "a b"], ids=["plain", "short", "inner-space"])
def test_raise_missing_system_error_contract(subtests, name) -> None:
    """Verify raise_missing_system_error produces a well-formed ParamError card that names the profile."""

    expected = "a full key 'system/name', or a system given separately"

    exc = assert_exception_function(
        subtests,
        raise_missing_system_error,
        invalid_params=(name,),
        exception_type=ParamError,
        error_name="EXTRACTOR_PROFILE_INVALID",
        label="profile keys",
        value=name,
        problem=f"The profile {name!r} has no system.",
        expected=expected,
        how_to_fix=f"Provide {expected}.",
        exception=ValueError,
        verbose=False,
    )

    # Catchable as the wrapped standard type and as "any error of this library"
    assert isinstance(exc, ValueError)
    assert isinstance(exc, SimpleError)
