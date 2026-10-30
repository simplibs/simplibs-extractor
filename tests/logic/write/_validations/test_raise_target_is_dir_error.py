from pathlib import Path
import pytest
from simplibs.exception import SimpleError, StateError
from simplibs.exception.testing import assert_exception_function
from simplibs.extractor.logic.write._validations import raise_target_is_dir_error


@pytest.mark.parametrize("path", [Path("out"), Path("a") / "b", Path("složka")])
def test_raise_target_is_dir_error_contract(subtests, path) -> None:
    """Verify raise_target_is_dir_error produces a well-formed StateError card that explains what `-o` takes."""

    exc = assert_exception_function(
        subtests,
        raise_target_is_dir_error,
        invalid_params=(path,),
        exception_type=StateError,
        error_name="EXTRACTOR_TARGET_IS_DIR",
        label=f"output '{path}'",
        value=str(path),
        problem=f"The output '{path}' is an existing directory, not a file.",
        expected="The path of a file, in a folder that exists or can be created.",
        how_to_fix=(
            "Pass a file path as the target (for example 'out/extraction.md').",
            "On the command line, -o takes a folder; the file name comes from the profile.",
        ),
        exception=IsADirectoryError,
        verbose=False,
    )

    # Catchable as the wrapped standard type and as "any error of this library"
    assert isinstance(exc, IsADirectoryError)
    assert isinstance(exc, SimpleError)
