from pathlib import Path
import pytest
from simplibs.exception import AlreadyExistsError, SimpleError
from simplibs.exception.testing import assert_exception_function
from simplibs.extractor.logic.write._validations import raise_target_exists_error


@pytest.mark.parametrize("path", [Path("extraction.md"), Path("out") / "extraction.md", Path("výstup") / "soubor.md"])
def test_raise_target_exists_error_contract(subtests, path) -> None:
    """Verify raise_target_exists_error produces a well-formed AlreadyExistsError card that names the four policies."""

    exc = assert_exception_function(
        subtests,
        raise_target_exists_error,
        invalid_params=(path,),
        exception_type=AlreadyExistsError,
        error_name="EXTRACTOR_TARGET_EXISTS",
        label=f"output '{path}'",
        value=str(path),
        problem=f"The output '{path}' already exists and the overwrite policy is 'error'.",
        expected="An output path that does not exist yet, or another overwrite policy.",
        how_to_fix=(
            "Use overwrite='overwrite' to replace it, 'unique' to write a numbered copy, or 'backup' to keep the old one.",
            "Choose a different output folder or name.",
        ),
        exception=FileExistsError,
        verbose=False,
    )

    # Catchable as the wrapped standard type and as "any error of this library"
    assert isinstance(exc, FileExistsError)
    assert isinstance(exc, SimpleError)
