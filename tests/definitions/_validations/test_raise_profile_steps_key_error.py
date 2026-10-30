import pytest
from simplibs.exception import ParamError, SimpleError
from simplibs.exception.testing import assert_exception_function
from simplibs.extractor.definitions._validations import raise_profile_steps_key_error


@pytest.mark.parametrize("value", [".PY", "py", ".", "", 3], ids=["uppercase", "no-dot", "dot-only", "empty", "not-a-string"])
def test_raise_profile_steps_key_error_contract(subtests, value) -> None:
    """Verify raise_profile_steps_key_error produces a well-formed ParamError card."""

    expected = "'*' or a lowercase suffix such as '.py'"

    exc = assert_exception_function(
        subtests,
        raise_profile_steps_key_error,
        invalid_params=(value,),
        exception_type=ParamError,
        error_name="EXTRACTOR_PROFILE_INVALID",
        label="profile steps key",
        value=value,
        problem=f"The steps key {value!r} can never match a file.",
        expected=expected,
        how_to_fix=f"Provide {expected}.",
        exception=ValueError,
        verbose=False,
    )

    # Catchable as the wrapped standard type and as "any error of this library"
    assert isinstance(exc, ValueError)
    assert isinstance(exc, SimpleError)
