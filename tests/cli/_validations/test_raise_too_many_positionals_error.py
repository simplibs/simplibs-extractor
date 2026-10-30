from pathlib import Path
import pytest
from simplibs.exception import ParamError, SimpleError
from simplibs.exception.testing import assert_exception_function
from simplibs.extractor.cli._validations import raise_too_many_positionals_error


@pytest.mark.parametrize(
    "system, profiles, source",
    [
        ("generic/all", "a", Path("src")),
        ("a,b", None, Path("x")),
        ("python/code-clean", "other", Path("a") / "b"),
    ],
    ids=["keys-and-two-words", "list-without-profiles", "nested-source"],
)
def test_raise_too_many_positionals_error_contract(subtests, system, profiles, source) -> None:
    """Verify raise_too_many_positionals_error produces a well-formed ParamError card; the value is the three words."""

    exc = assert_exception_function(
        subtests,
        raise_too_many_positionals_error,
        invalid_params=(system, profiles, source),
        exception_type=ParamError,
        error_name="EXTRACTOR_CONFIG_INVALID",
        label="command-line arguments",
        value=[system, profiles, str(source)],
        problem="Full profile keys were followed by two more words.",
        expected="KEYS [SOURCE] or SYSTEM PROFILES [SOURCE].",
        how_to_fix="Write 'generic/all ./src', or 'python code-clean ./src'.",
        exception=ValueError,
        verbose=False,
    )

    # Catchable as the wrapped standard type and as "any error of this library"
    assert isinstance(exc, ValueError)
    assert isinstance(exc, SimpleError)
