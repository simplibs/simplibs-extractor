import pytest
from simplibs.exception import NotFoundError, SimpleError
from simplibs.exception.testing import assert_exception_function
from simplibs.extractor.registry._validations import raise_profile_not_found_error


@pytest.mark.parametrize(
    "key, known, listed",
    [
        ("python/nope", [], "(none registered)"),
        ("python/nope", ["python/code-clean"], "python/code-clean"),
        ("a/x", ["a/y", "b/z", "generic/all"], "a/y, b/z, generic/all"),
        ("", ("generic/all",), "generic/all"),
    ],
    ids=["none-registered", "one-registered", "several-registered", "tuple-of-keys"],
)
def test_raise_profile_not_found_error_contract(subtests, key, known, listed) -> None:
    """Verify raise_profile_not_found_error produces a well-formed NotFoundError card that names what IS registered."""

    exc = assert_exception_function(
        subtests,
        raise_profile_not_found_error,
        invalid_params=(key, known),
        exception_type=NotFoundError,
        error_name="EXTRACTOR_PROFILE_NOT_FOUND",
        label=f"profile '{key}'",
        value=key,
        problem=f"No profile is registered under '{key}'.",
        expected=f"One of the registered profiles: {listed}.",
        how_to_fix=(
            "Check the spelling of the key ('system/name').",
            "Install the package that provides the profile (for example simplibs-code-extractor).",
        ),
        exception=LookupError,
        verbose=False,
    )

    # Catchable as the wrapped standard type and as "any error of this library"
    assert isinstance(exc, LookupError)
    assert isinstance(exc, SimpleError)
