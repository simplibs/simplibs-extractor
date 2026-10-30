import pytest
from simplibs.exception import AlreadyExistsError, SimpleError
from simplibs.exception.testing import assert_exception_function
from simplibs.extractor.registry._validations import raise_profile_exists_error


@pytest.mark.parametrize("key", ["python/code-clean", "generic/all", "a/b"])
def test_raise_profile_exists_error_contract(subtests, key) -> None:
    """Verify raise_profile_exists_error produces a well-formed AlreadyExistsError card."""

    exc = assert_exception_function(
        subtests,
        raise_profile_exists_error,
        invalid_params=(key,),
        exception_type=AlreadyExistsError,
        error_name="EXTRACTOR_PROFILE_EXISTS",
        label=f"profile '{key}'",
        value=key,
        problem=f"A profile is already registered under '{key}'.",
        expected="A key that is not registered yet, or replace_existing=True.",
        how_to_fix=(
            "Pass replace_existing=True if replacing the profile is intended.",
            "Choose a different name for the new profile.",
        ),
        exception=ValueError,
        verbose=False,
    )

    # Catchable as the wrapped standard type and as "any error of this library"
    assert isinstance(exc, ValueError)
    assert isinstance(exc, SimpleError)
