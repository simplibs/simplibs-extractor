import pytest
from simplibs.exception import ParamError, SimpleError
from simplibs.exception.testing import assert_exception_function
from simplibs.extractor.scripts._validations import raise_invalid_output_name_error


@pytest.mark.parametrize("name", ["a/b.md", "", "x\\y.md", "con?.md"], ids=["slash", "empty", "backslash", "forbidden-char"])
def test_raise_invalid_output_name_error_contract(subtests, name) -> None:
    """Verify raise_invalid_output_name_error produces a well-formed ParamError card."""

    exc = assert_exception_function(
        subtests,
        raise_invalid_output_name_error,
        invalid_params=(name,),
        exception_type=ParamError,
        error_name="EXTRACTOR_CONFIG_INVALID",
        label="parameter 'output_name'",
        value=name,
        problem=f"{name!r} is not a usable file name.",
        expected="A plain file name such as 'extraction.md' (no folders).",
        how_to_fix="Pass only a name, or give a full path through target=... instead.",
        exception=ValueError,
        verbose=False,
    )

    # Catchable as the wrapped standard type and as "any error of this library"
    assert isinstance(exc, ValueError)
    assert isinstance(exc, SimpleError)
