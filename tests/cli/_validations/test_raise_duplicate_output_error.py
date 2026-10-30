import pytest
from simplibs.exception import ParamError, SimpleError
from simplibs.exception.testing import assert_exception_function
from simplibs.extractor.cli._validations import raise_duplicate_output_error


@pytest.mark.parametrize(
    "keys",
    [["a/x", "b/y"], ("a/x", "a/y"), ["generic/all"]],
    ids=["list", "tuple", "single"],
)
def test_raise_duplicate_output_error_contract(subtests, keys) -> None:
    """Verify raise_duplicate_output_error produces a well-formed ParamError card; the value is the keys as a list."""

    exc = assert_exception_function(
        subtests,
        raise_duplicate_output_error,
        invalid_params=(keys,),
        exception_type=ParamError,
        error_name="EXTRACTOR_CONFIG_INVALID",
        label="profiles",
        value=list(keys),
        problem="Two or more of these profiles write the same output file.",
        expected="Profiles with different output names, or one profile per run.",
        how_to_fix="Run the profiles separately, or give them different output_name values.",
        exception=ValueError,
        verbose=False,
    )

    # Catchable as the wrapped standard type and as "any error of this library"
    assert isinstance(exc, ValueError)
    assert isinstance(exc, SimpleError)
