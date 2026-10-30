from pathlib import Path
import pytest
from simplibs.exception import ParamError, SimpleError
from simplibs.exception.testing import assert_exception_function
from simplibs.extractor.scripts._validations import raise_not_python_script_error


@pytest.mark.parametrize(
    "target",
    [Path("script.txt"), Path("a") / "run", Path("x.PY"), Path("with space.sh")],
    ids=["txt", "no-suffix", "uppercase-suffix", "shell"],
)
def test_raise_not_python_script_error_contract(subtests, target) -> None:
    """Verify raise_not_python_script_error produces a well-formed ParamError card; the value is the path as text."""

    exc = assert_exception_function(
        subtests,
        raise_not_python_script_error,
        invalid_params=(target,),
        exception_type=ParamError,
        error_name="EXTRACTOR_CONFIG_INVALID",
        label="parameter 'path'",
        value=str(target),
        problem=f"The script name {target.name!r} does not end with '.py'.",
        expected="A file name ending with '.py', or a folder.",
        how_to_fix="Add '.py' to the name, or pass the folder the script should lie in.",
        exception=ValueError,
        verbose=False,
    )

    # Catchable as the wrapped standard type and as "any error of this library"
    assert isinstance(exc, ValueError)
    assert isinstance(exc, SimpleError)
