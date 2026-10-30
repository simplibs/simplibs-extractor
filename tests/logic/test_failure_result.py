from pathlib import Path
import pytest
from simplibs.exception import SimpleException
from simplibs.extractor.constants import DEFAULT_PROFILE_KEY
from simplibs.extractor.definitions import ExtractionConfig, Profile
from simplibs.extractor.registry._validations import raise_profile_not_found_error
from simplibs.extractor.logic.select._validations import raise_source_not_found_error
from simplibs.extractor.logic.write._validations import raise_target_exists_error
from simplibs.extractor.logic._common import describe_failure
from simplibs.extractor.logic import failure_result


def _card() -> SimpleException:
    try:
        raise_source_not_found_error(Path("missing"))
    except SimpleException as caught:
        return caught
    raise AssertionError("the card was not raised")


def test_failure_result_carries_the_config_and_a_one_line_reason(tmp_path) -> None:
    """The run that could not start becomes a result, with the reason in `fatal`."""
    config = ExtractionConfig(source=tmp_path)
    error = _card()

    result = failure_result(config, error)

    assert result.config is config
    assert result.fatal == describe_failure(error)
    assert result.fatal.startswith("NotFoundError: ")
    assert "\n" not in result.fatal


def test_failure_result_has_no_output_and_no_files(tmp_path) -> None:
    """Everything else stays at its empty default."""
    result = failure_result(ExtractionConfig(source=tmp_path), _card())

    assert result.target is None
    assert result.written is False
    assert result.files == ()
    assert (result.bytes_in, result.bytes_out, result.tokens_estimate) == (0, 0, 0)
    assert result.duration == 0.0


def test_failure_result_is_never_a_success(tmp_path) -> None:
    """A result with a fatal reason does not count as done."""
    result = failure_result(ExtractionConfig(source=tmp_path), _card())

    assert result.success is False
    assert result.ok_files == () and result.error_files == () and result.skipped_files == ()


@pytest.mark.parametrize("dry_run", [True, False])
def test_failure_result_keeps_the_dry_run_flag(tmp_path, dry_run) -> None:
    """The report can still say that nothing was meant to be written."""
    result = failure_result(ExtractionConfig(source=tmp_path, dry_run=dry_run), _card())

    assert result.dry_run is dry_run


def test_failure_result_without_a_profile_names_the_default_one(tmp_path) -> None:
    """`None` means `generic/all`."""
    result = failure_result(ExtractionConfig(source=tmp_path, profile=None), _card())

    assert result.profile_key == DEFAULT_PROFILE_KEY


def test_failure_result_a_profile_given_as_a_key_is_named_as_typed(tmp_path) -> None:
    """The key is not looked up: the run failed before anything was resolved, and an unknown key is the typical reason."""
    result = failure_result(ExtractionConfig(source=tmp_path, profile="python/no-such-profile"), _card())

    assert result.profile_key == "python/no-such-profile"


def test_failure_result_a_profile_object_is_named_by_its_key(tmp_path) -> None:
    """A `Profile` knows its own key."""
    profile = Profile(system="demo", name="steps")

    result = failure_result(ExtractionConfig(source=tmp_path, profile=profile), _card())

    assert result.profile_key == "demo/steps"


@pytest.mark.parametrize(
    "raiser, class_name",
    [
        (lambda: raise_target_exists_error(Path("out.md")), "AlreadyExistsError"),
        (lambda: raise_profile_not_found_error("a/b", ["generic/all"]), "NotFoundError"),
        (lambda: raise_source_not_found_error(Path("x")), "NotFoundError"),
    ],
    ids=["exists", "profile-not-found", "source-not-found"],
)
def test_failure_result_describes_any_card_of_the_library(tmp_path, raiser, class_name) -> None:
    """The reason always starts with the class of the card."""
    try:
        raiser()
    except SimpleException as error:
        result = failure_result(ExtractionConfig(source=tmp_path), error)

    assert result.fatal.startswith(class_name)
