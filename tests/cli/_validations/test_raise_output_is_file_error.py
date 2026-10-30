from pathlib import Path
import pytest
from simplibs.exception import ParamError, SimpleError
from simplibs.exception.testing import assert_exception_function
from simplibs.extractor.cli._validations import raise_output_is_file_error


@pytest.mark.parametrize(
    "out_dir",
    [Path("out.md"), Path("a") / "b" / "c.txt", Path("a folder with spaces"), Path("příliš")],
    ids=["simple", "nested", "spaces", "non-ascii"],
)
def test_raise_output_is_file_error_contract(subtests, out_dir) -> None:
    """Verify raise_output_is_file_error produces a well-formed ParamError card; the value is the path as text."""

    exc = assert_exception_function(
        subtests,
        raise_output_is_file_error,
        invalid_params=(out_dir,),
        exception_type=ParamError,
        error_name="EXTRACTOR_CONFIG_INVALID",
        label="option '-o'",
        value=str(out_dir),
        problem=f"'{out_dir}' is a file, but -o takes a folder.",
        expected="A folder (existing or to be created).",
        how_to_fix="Pass a folder; the file name comes from the profile.",
        exception=ValueError,
        verbose=False,
    )

    # Catchable as the wrapped standard type and as "any error of this library"
    assert isinstance(exc, ValueError)
    assert isinstance(exc, SimpleError)
