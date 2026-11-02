from simplibs.exception import ParamError
from simplibs.exception.testing import assert_exception_function
from simplibs.extractor.registry._validations import raise_language_name_error


def test_raise_language_name_error_card(subtests) -> None:
    assert_exception_function(
        subtests,
        raise_language_name_error,
        invalid_params=("a b",),
        exception_type=ParamError,
        error_name="EXTRACTOR_CONFIG_INVALID",
        label="parameter 'language'",
        value="a b",
        problem="'a b' cannot be written after a code fence.",
        exception=ValueError,
        verbose=False,
    )
