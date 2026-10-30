import pytest
from simplibs.exception import ParamError, SimpleError
from simplibs.exception.testing import assert_exception_function
from simplibs.extractor.definitions._validations import raise_profile_key_part_error


@pytest.mark.parametrize(
    "part_name, value",
    [
        ("system", "a/b"),
        ("system", ""),
        ("name", "code clean"),
        ("name", None),
        ("name", "a,b"),
    ],
    ids=["system-slash", "system-empty", "name-space", "name-none", "name-comma"],
)
def test_raise_profile_key_part_error_contract(subtests, part_name, value) -> None:
    """Verify raise_profile_key_part_error produces a well-formed ParamError card for either half of a key."""

    expected = f"a non-blank {part_name} without '/', ',' or whitespace"

    exc = assert_exception_function(
        subtests,
        raise_profile_key_part_error,
        invalid_params=(part_name, value),
        exception_type=ParamError,
        error_name="EXTRACTOR_PROFILE_INVALID",
        label=f"profile {part_name}",
        value=value,
        problem=f"The {part_name} {value!r} cannot be a part of a profile key.",
        expected=expected,
        how_to_fix=f"Provide {expected}.",
        exception=ValueError,
        verbose=False,
    )

    # Catchable as the wrapped standard type and as "any error of this library"
    assert isinstance(exc, ValueError)
    assert isinstance(exc, SimpleError)
