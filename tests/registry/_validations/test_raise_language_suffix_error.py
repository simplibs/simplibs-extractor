from simplibs.exception import ParamError
from simplibs.exception.testing import assert_exception_function
from simplibs.extractor.registry._validations import raise_language_suffix_error


def test_raise_language_suffix_error_card(subtests) -> None:
    assert_exception_function(
        subtests,
        raise_language_suffix_error,
        invalid_params=("py",),
        exception_type=ParamError,
        error_name="EXTRACTOR_CONFIG_INVALID",
        label="parameter 'suffix'",
        value="py",
        problem="'py' is not a usable file suffix.",
        exception=ValueError,
        verbose=False,
    )
