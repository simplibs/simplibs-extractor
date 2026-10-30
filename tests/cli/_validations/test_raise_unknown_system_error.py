import pytest
from simplibs.exception import ParamError, SimpleError
from simplibs.exception.testing import assert_exception_function
from simplibs.extractor.cli._helpers import system_options
from simplibs.extractor.cli._validations import raise_unknown_system_error


@pytest.mark.parametrize("system", ["nope", "PYTHON", ""], ids=["unknown", "wrong-case", "empty"])
def test_raise_unknown_system_error_contract(subtests, system) -> None:
    """Verify raise_unknown_system_error produces a well-formed ParamError card listing the registered systems."""

    listed = ", ".join(system_options()) or "(none)"

    exc = assert_exception_function(
        subtests,
        raise_unknown_system_error,
        invalid_params=(system,),
        exception_type=ParamError,
        error_name="EXTRACTOR_CONFIG_INVALID",
        label="system",
        value=system,
        problem=f"No profile is registered for the system {system!r}.",
        expected=f"One of the registered systems: {listed}.",
        how_to_fix="Check the spelling, or install the package that provides the system.",
        exception=ValueError,
        verbose=False,
    )

    # Catchable as the wrapped standard type and as "any error of this library"
    assert isinstance(exc, ValueError)
    assert isinstance(exc, SimpleError)
