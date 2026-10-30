import argparse
from pathlib import Path
import pytest
from simplibs.exception import NotFoundError, ParamError
from simplibs.exception.testing import assert_exception_function
from simplibs.extractor.cli import build_configs, build_parser
from simplibs.extractor.definitions import ExtractionConfig, Profile
from simplibs.extractor.registry import register_profile
from simplibs.path import normalize_path


@pytest.fixture
def source(tmp_path) -> Path:
    folder = tmp_path / "project"
    folder.mkdir()
    return folder


@pytest.fixture(autouse=True)
def some_profiles():
    register_profile(Profile("t", "a", output_name="a.md"))
    register_profile(Profile("t", "b", output_name="b.txt", format="plain"))
    register_profile(Profile("t", "also-default"))        # writes the default output name, like generic/all


def _args(*argv: str) -> argparse.Namespace:
    return build_parser().parse_args(list(argv))


# ---------------------------------------------------------------- one config per key

def test_one_key_gives_one_config(source) -> None:
    configs = build_configs(_args(), ["t/a"], source, False)
    assert len(configs) == 1
    assert isinstance(configs[0], ExtractionConfig)


def test_the_config_carries_the_key_and_the_source(source) -> None:
    config = build_configs(_args(), ["t/a"], source, False)[0]
    assert config.profile == "t/a"
    assert config.source == source


def test_the_output_goes_next_to_the_source_under_the_name_of_the_profile(source) -> None:
    config = build_configs(_args(), ["t/a"], source, False)[0]
    assert config.target == normalize_path(source) / "a.md"


def test_the_configs_follow_the_order_of_the_keys(source) -> None:
    configs = build_configs(_args(), ["t/b", "t/a"], source, False)
    assert [config.profile for config in configs] == ["t/b", "t/a"]
    assert [config.target.name for config in configs] == ["b.txt", "a.md"]


def test_no_keys_give_no_configs(source) -> None:
    assert build_configs(_args(), [], source, False) == []


# ---------------------------------------------------------------- the options of the command

def test_defaults_of_the_command_reach_the_config(source) -> None:
    config = build_configs(_args(), ["t/a"], source, False)[0]
    assert config.format is None
    assert config.overwrite == "overwrite"
    assert config.add_tree is True
    assert config.dry_run is False


def test_format_overwrite_and_tree_reach_the_config(source) -> None:
    config = build_configs(_args("--format", "plain", "--overwrite", "unique", "--no-tree"), ["t/a"], source, False)[0]
    assert config.format == "plain"
    assert config.overwrite == "unique"
    assert config.add_tree is False


@pytest.mark.parametrize("dry_run", [True, False])
def test_the_decision_about_the_dry_run_is_the_argument_not_the_flag(source, dry_run) -> None:
    config = build_configs(_args(), ["t/a"], source, dry_run)[0]
    assert config.dry_run is dry_run


def test_every_config_gets_the_same_options(source) -> None:
    configs = build_configs(_args("--overwrite", "backup", "--no-tree"), ["t/a", "t/b"], source, True)
    assert {config.overwrite for config in configs} == {"backup"}
    assert {config.add_tree for config in configs} == {False}
    assert {config.dry_run for config in configs} == {True}


# ---------------------------------------------------------------- -o

def test_o_is_the_output_folder(source, tmp_path) -> None:
    out = tmp_path / "out"
    configs = build_configs(_args("-o", str(out)), ["t/a", "t/b"], source, False)
    assert [config.target for config in configs] == [normalize_path(out) / "a.md", normalize_path(out) / "b.txt"]


def test_the_output_folder_need_not_exist(source, tmp_path) -> None:
    out = tmp_path / "does" / "not" / "exist"
    config = build_configs(_args("-o", str(out)), ["t/a"], source, False)[0]
    assert config.target == normalize_path(out) / "a.md"
    assert not out.exists()


def test_a_relative_output_folder_is_made_absolute(source, tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    config = build_configs(_args("-o", "out"), ["t/a"], source, False)[0]
    assert config.target == normalize_path(tmp_path / "out") / "a.md"


def test_an_output_that_is_a_file_gives_a_config_card(subtests, source, tmp_path) -> None:
    file = tmp_path / "result.md"
    file.write_text("x\n", encoding="utf-8")
    assert_exception_function(
        subtests,
        lambda out: build_configs(_args("-o", str(out)), ["t/a"], source, False),
        invalid_params=(file,),
        valid_params=(tmp_path / "folder",),
        exception_type=ParamError,
        error_name="EXTRACTOR_CONFIG_INVALID",
        label="option '-o'",
        value=str(normalize_path(file)),
        problem=f"'{normalize_path(file)}' is a file, but -o takes a folder.",
        verbose=False,
    )


# ---------------------------------------------------------------- refusals

def test_an_unknown_key_is_refused_before_anything_runs(source) -> None:
    with pytest.raises(NotFoundError) as caught:
        build_configs(_args(), ["t/a", "t/nothing"], source, False)
    assert caught.value.error_name == "EXTRACTOR_PROFILE_NOT_FOUND"


def test_two_profiles_with_one_output_name_are_refused(subtests, source) -> None:
    assert_exception_function(
        subtests,
        lambda *keys: build_configs(_args(), list(keys), source, False),
        invalid_params=("generic/all", "t/also-default"),
        valid_params=("generic/all", "t/a"),
        exception_type=ParamError,
        error_name="EXTRACTOR_CONFIG_INVALID",
        label="profiles",
        value=["generic/all", "t/also-default"],
        problem="Two or more of these profiles write the same output file.",
        verbose=False,
    )


def test_the_same_key_twice_is_refused(source) -> None:
    with pytest.raises(ParamError):
        build_configs(_args(), ["t/a", "t/a"], source, False)


def test_with_o_the_profiles_still_share_one_folder_so_one_name_is_still_refused(source, tmp_path) -> None:
    """With -o every profile goes to the same folder, so the check is the same as without it."""
    with pytest.raises(ParamError):
        build_configs(_args("-o", str(tmp_path / "out")), ["generic/all", "t/also-default"], source, False)
