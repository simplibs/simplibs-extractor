from simplibs.exception import ParamError
from simplibs.exception.testing import assert_exception_function
from simplibs.extractor.registry._validations import raise_language_exists_error


def test_raise_language_exists_error_card(subtests) -> None:
    assert_exception_function(
        subtests,
        raise_language_exists_error,
        invalid_params=(".py",),
        exception_type=ParamError,
        error_name="EXTRACTOR_CONFIG_INVALID",
        label="language of '.py'",
        value=".py",
        problem="A language is already registered for the suffix '.py'.",
        expected="A suffix that has no language yet, or replace_existing=True.",
        how_to_fix="Pass replace_existing=True, or choose a different suffix.",
        exception=ValueError,
        verbose=False,
    )
