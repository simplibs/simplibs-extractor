from simplibs.exception import ParamError, SimpleError
from simplibs.exception.testing import assert_exception_function
from simplibs.extractor.logic.select._validations import raise_missing_source_error


def test_raise_missing_source_error_contract(subtests) -> None:
    """Verify raise_missing_source_error produces a well-formed ParamError card (it takes no arguments)."""

    exc = assert_exception_function(
        subtests,
        raise_missing_source_error,
        invalid_params=(),
        exception_type=ParamError,
        error_name="EXTRACTOR_CONFIG_INVALID",
        label="parameter 'source'",
        value=None,
        problem="No config and no 'source' were given.",
        expected="An ExtractionConfig, or at least source='path/to/folder'.",
        how_to_fix="Pass a config, or pass source=... as a keyword.",
        exception=ValueError,
        verbose=False,
    )

    # Catchable as the wrapped standard type and as "any error of this library"
    assert isinstance(exc, ValueError)
    assert isinstance(exc, SimpleError)
