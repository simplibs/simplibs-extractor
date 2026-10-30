from pathlib import Path
import pytest
from simplibs.exception import NotFoundError, SimpleError
from simplibs.exception.testing import assert_exception_function
from simplibs.extractor.logic.select._validations import raise_source_not_found_error


@pytest.mark.parametrize("path", [Path("missing"), Path("a") / "b" / "c", Path("a folder with spaces"), Path("příliš")])
def test_raise_source_not_found_error_contract(subtests, path) -> None:
    """Verify raise_source_not_found_error produces a well-formed NotFoundError card; the value is the path as text."""

    exc = assert_exception_function(
        subtests,
        raise_source_not_found_error,
        invalid_params=(path,),
        exception_type=NotFoundError,
        error_name="EXTRACTOR_SOURCE_NOT_FOUND",
        label=f"source '{path}'",
        value=str(path),
        problem=f"'{path}' is not an existing directory.",
        expected="The path of an existing directory to extract from.",
        how_to_fix=(
            "Check the path for typos.",
            "Create the directory, or point 'source' at the folder that holds the files.",
        ),
        exception=FileNotFoundError,
        verbose=False,
    )

    # Catchable as the wrapped standard type and as "any error of this library"
    assert isinstance(exc, FileNotFoundError)
    assert isinstance(exc, SimpleError)
