import dataclasses
from pathlib import Path
import pytest
from simplibs.exception import NotFoundError, ParamError, ValidationError
from simplibs.exception.testing import assert_exception_function
from simplibs.path import normalize_path
from simplibs.extractor.constants import DEFAULT_OUTPUT_NAME
from simplibs.extractor.definitions import ExtractionConfig, Profile, Resolved
from simplibs.extractor.logic.select import resolve_config
from simplibs.extractor.registry import register_profile
from simplibs.extractor.registry._helpers import GENERIC_ALL

CONFIG_FIELDS = (
    "add_tree", "dry_run", "exclude", "format", "ignore_names", "include", "max_file_size",
    "overwrite", "profile", "recursive", "skip_paths", "source", "target", "title",
)


@pytest.fixture
def source(tmp_path) -> Path:
    folder = tmp_path / "project"
    folder.mkdir()
    return folder


# ---------------------------------------------------------------- the happy path

def test_source_alone_is_enough(source) -> None:
    resolved = resolve_config(None, {"source": source})
    assert isinstance(resolved, Resolved)
    assert resolved.profile is GENERIC_ALL
    assert resolved.format == "markdown"


def test_source_is_normalized(source) -> None:
    resolved = resolve_config(None, {"source": str(source)})
    assert resolved.config.source == normalize_path(source)
    assert isinstance(resolved.config.source, Path)
    assert resolved.config.source.is_absolute()


def test_relative_source_is_resolved_against_the_working_folder(source, monkeypatch) -> None:
    monkeypatch.chdir(source.parent)
    resolved = resolve_config(None, {"source": "project"})
    assert resolved.config.source == normalize_path(source)


def test_default_target_is_the_profile_output_inside_the_source(source) -> None:
    resolved = resolve_config(None, {"source": source})
    assert resolved.config.target == resolved.config.source / DEFAULT_OUTPUT_NAME


def test_default_target_follows_the_output_name_of_the_profile(source) -> None:
    profile = Profile("python", "dump", output_name="dump.txt")
    resolved = resolve_config(None, {"source": source, "profile": profile})
    assert resolved.config.target == resolved.config.source / "dump.txt"


def test_given_target_is_normalized(source, monkeypatch) -> None:
    monkeypatch.chdir(source)
    resolved = resolve_config(None, {"source": source, "target": "out.md"})
    assert resolved.config.target == normalize_path("out.md")
    assert resolved.config.target.is_absolute()


def test_other_fields_are_kept(source) -> None:
    resolved = resolve_config(
        None, {"source": source, "title": "My code", "dry_run": True, "overwrite": "unique", "add_tree": False}
    )
    assert resolved.config.title == "My code"
    assert resolved.config.dry_run is True
    assert resolved.config.overwrite == "unique"
    assert resolved.config.add_tree is False


# ---------------------------------------------------------------- profile and format

def test_profile_key_gives_the_registered_profile(source) -> None:
    registered = register_profile(Profile("python", "code"))
    assert resolve_config(None, {"source": source, "profile": "python/code"}).profile is registered


def test_profile_object_is_used_as_it_is(source) -> None:
    profile = Profile("python", "unregistered")
    assert resolve_config(None, {"source": source, "profile": profile}).profile is profile


def test_format_of_the_profile_is_the_default(source) -> None:
    profile = Profile("python", "plain-one", format="plain")
    assert resolve_config(None, {"source": source, "profile": profile}).format == "plain"


def test_format_of_the_config_wins_over_the_profile(source) -> None:
    profile = Profile("python", "plain-one", format="plain")
    assert resolve_config(None, {"source": source, "profile": profile, "format": "markdown"}).format == "markdown"


def test_unknown_profile_gives_a_not_found_card(source, subtests) -> None:
    assert_exception_function(
        subtests,
        lambda key: resolve_config(None, {"source": source, "profile": key}),
        invalid_params=("python/missing",),
        valid_params=("generic/all",),
        exception_type=NotFoundError,
        error_name="EXTRACTOR_PROFILE_NOT_FOUND",
        value="python/missing",
        verbose=False,
    )


def test_unregistered_format_of_the_config_gives_a_config_invalid_card(source, subtests) -> None:
    assert_exception_function(
        subtests,
        lambda name: resolve_config(None, {"source": source, "format": name}),
        invalid_params=("pdf",),
        valid_params=("plain",),
        exception_type=ParamError,
        error_name="EXTRACTOR_CONFIG_INVALID",
        label="parameter 'format'",
        value="pdf",
        problem="No renderer is registered for the format 'pdf'.",
        verbose=False,
    )


def test_unregistered_format_of_the_profile_is_found_too(source, subtests) -> None:
    profile = Profile("python", "pdf-one", format="pdf")
    assert_exception_function(
        subtests,
        lambda: resolve_config(None, {"source": source, "profile": profile}),
        invalid_params=(),
        exception_type=ParamError,
        error_name="EXTRACTOR_CONFIG_INVALID",
        value="pdf",
        verbose=False,
    )


# ---------------------------------------------------------------- the source

def test_missing_source_folder_gives_a_not_found_card(tmp_path, subtests) -> None:
    missing = tmp_path / "missing"
    assert_exception_function(
        subtests,
        lambda path: resolve_config(None, {"source": path}),
        invalid_params=(missing,),
        valid_params=(tmp_path,),
        exception_type=NotFoundError,
        error_name="EXTRACTOR_SOURCE_NOT_FOUND",
        label=f"source '{normalize_path(missing)}'",
        value=str(normalize_path(missing)),
        verbose=False,
    )


def test_a_file_is_not_a_source(tmp_path, subtests) -> None:
    file = tmp_path / "a.txt"
    file.write_text("x", encoding="utf-8")
    assert_exception_function(
        subtests,
        lambda path: resolve_config(None, {"source": path}),
        invalid_params=(file,),
        exception_type=NotFoundError,
        error_name="EXTRACTOR_SOURCE_NOT_FOUND",
        verbose=False,
    )


# ---------------------------------------------------------------- parameters that are not config fields

def test_the_known_parameters_are_exactly_the_config_fields() -> None:
    """The set of fields is the public list of parameters of extract(); a change must be a deliberate one."""
    assert tuple(sorted(field.name for field in dataclasses.fields(ExtractionConfig))) == CONFIG_FIELDS


def test_unknown_parameter_gives_a_config_invalid_card(source, subtests) -> None:
    assert_exception_function(
        subtests,
        lambda overrides: resolve_config(None, overrides),
        invalid_params=({"source": source, "sourc": 1},),
        valid_params=({"source": source},),
        exception_type=ParamError,
        error_name="EXTRACTOR_CONFIG_INVALID",
        label="extraction parameters",
        value=["sourc"],
        problem="Unknown parameter(s): sourc.",
        expected="Only these parameters: " + ", ".join(CONFIG_FIELDS) + ".",
        verbose=False,
    )


def test_every_unknown_parameter_is_named_sorted(source, subtests) -> None:
    assert_exception_function(
        subtests,
        lambda overrides: resolve_config(None, overrides),
        invalid_params=({"source": source, "zeta": 1, "alpha": 2},),
        exception_type=ParamError,
        error_name="EXTRACTOR_CONFIG_INVALID",
        value=["alpha", "zeta"],
        problem="Unknown parameter(s): alpha, zeta.",
        verbose=False,
    )


def test_unknown_parameter_is_found_even_with_a_ready_config(source) -> None:
    with pytest.raises(ParamError):
        resolve_config(ExtractionConfig(source=source), {"typo": 1})


def test_unknown_parameter_is_reported_before_a_missing_source(subtests) -> None:
    assert_exception_function(
        subtests,
        lambda overrides: resolve_config(None, overrides),
        invalid_params=({"typo": 1},),
        exception_type=ParamError,
        error_name="EXTRACTOR_CONFIG_INVALID",
        label="extraction parameters",
        verbose=False,
    )


# ---------------------------------------------------------------- no config and no source

@pytest.mark.parametrize("overrides", [{}, {"dry_run": True}, {"title": "T"}])
def test_no_config_and_no_source_gives_a_config_invalid_card(subtests, overrides) -> None:
    assert_exception_function(
        subtests,
        lambda values: resolve_config(None, values),
        invalid_params=(overrides,),
        exception_type=ParamError,
        error_name="EXTRACTOR_CONFIG_INVALID",
        label="parameter 'source'",
        value=None,
        problem="No config and no 'source' were given.",
        expected="An ExtractionConfig, or at least source='path/to/folder'.",
        how_to_fix="Pass a config, or pass source=... as a keyword.",
        verbose=False,
    )


# ---------------------------------------------------------------- a ready config with overrides

def test_ready_config_without_overrides_is_resolved_as_it_is(source) -> None:
    config = ExtractionConfig(source=source, title="T")
    resolved = resolve_config(config, {})
    assert resolved.config.title == "T"
    assert resolved.config.source == normalize_path(source)


def test_overrides_change_the_ready_config(source) -> None:
    config = ExtractionConfig(source=source, dry_run=False, title="T")
    resolved = resolve_config(config, {"dry_run": True})
    assert resolved.config.dry_run is True
    assert resolved.config.title == "T"


def test_ready_config_itself_is_not_changed(source) -> None:
    config = ExtractionConfig(source=source)
    resolve_config(config, {"dry_run": True})
    assert config.dry_run is False
    assert config.source == source


def test_a_bad_override_is_rejected_like_a_bad_config_value(source) -> None:
    with pytest.raises(ValidationError):
        resolve_config(ExtractionConfig(source=source), {"overwrite": "force"})


def test_a_bad_value_without_a_config_is_rejected_too(source) -> None:
    with pytest.raises(ValidationError):
        resolve_config(None, {"source": source, "overwrite": "force"})


def test_the_source_can_be_overridden(source, tmp_path) -> None:
    other = tmp_path / "other"
    other.mkdir()
    resolved = resolve_config(ExtractionConfig(source=source), {"source": other})
    assert resolved.config.source == normalize_path(other)
