import argparse
from pathlib import Path
import pytest
from simplibs.exception import ParamError
from simplibs.exception.testing import assert_exception_function
from simplibs.extractor.cli import build_parser, normalize_positionals
from simplibs.extractor.definitions import Profile
from simplibs.extractor.registry import register_profile


@pytest.fixture(autouse=True)
def in_a_project(tmp_path, monkeypatch):
    """A working folder with a folder `src`, `src/sub` and a file `notes.txt`."""
    (tmp_path / "src" / "sub").mkdir(parents=True)
    (tmp_path / "notes.txt").write_text("x\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    return tmp_path


def _normalized(*argv: str) -> argparse.Namespace:
    return normalize_positionals(build_parser().parse_args(list(argv)))


def _roles(args: argparse.Namespace):
    return args.system, args.profiles, args.source


# ---------------------------------------------------------------- one word

def test_nothing_typed_changes_nothing() -> None:
    assert _roles(_normalized()) == (None, None, None)


def test_a_single_folder_is_the_source() -> None:
    assert _roles(_normalized("src")) == (None, None, Path("src"))


@pytest.mark.parametrize("word", ["./src", "src/sub", "."])
def test_a_single_folder_written_with_a_path_is_the_source(word) -> None:
    assert _roles(_normalized(word)) == (None, None, Path(word))


def test_a_single_word_that_is_no_folder_stays_a_system() -> None:
    """It will be refused later as an unknown system - with a card that names the known ones."""
    assert _roles(_normalized("nothing")) == ("nothing", None, None)


def test_a_file_is_no_source() -> None:
    assert _roles(_normalized("notes.txt")) == ("notes.txt", None, None)


def test_a_registered_system_wins_over_a_folder_of_the_same_name(in_a_project) -> None:
    register_profile(Profile("python", "a"))
    (in_a_project / "python").mkdir()
    assert _roles(_normalized("python")) == ("python", None, None)


def test_a_registered_profile_key_wins_over_a_folder_of_the_same_name(in_a_project) -> None:
    (in_a_project / "generic" / "all").mkdir(parents=True)
    assert _roles(_normalized("generic/all")) == (None, "generic/all", None)


# ---------------------------------------------------------------- full keys first

def test_a_full_key_alone_is_the_profiles() -> None:
    assert _roles(_normalized("generic/all")) == (None, "generic/all", None)


def test_a_full_key_and_a_folder() -> None:
    assert _roles(_normalized("generic/all", "src")) == (None, "generic/all", Path("src"))


def test_a_comma_list_of_full_keys() -> None:
    assert _roles(_normalized("python/a,web/b", "src")) == (None, "python/a,web/b", Path("src"))


def test_an_unknown_full_key_is_still_taken_as_profiles() -> None:
    """Whether the key exists is asked later, by the registry, with a proper card."""
    assert _roles(_normalized("python/nothing")) == (None, "python/nothing", None)


def test_a_path_that_is_not_a_folder_is_taken_as_profiles_too() -> None:
    assert _roles(_normalized("no/such/folder")) == (None, "no/such/folder", None)


def test_full_keys_followed_by_two_words_are_refused(subtests) -> None:
    assert_exception_function(
        subtests,
        lambda *argv: _normalized(*argv),
        invalid_params=("generic/all", "a", "b"),
        valid_params=("generic/all", "b"),
        exception_type=ParamError,
        error_name="EXTRACTOR_CONFIG_INVALID",
        label="command-line arguments",
        value=["generic/all", "a", "b"],
        problem="Full profile keys were followed by two more words.",
        expected="KEYS [SOURCE] or SYSTEM PROFILES [SOURCE].",
        verbose=False,
    )


# ---------------------------------------------------------------- the usual order stays

def test_system_profiles_and_source_stay_as_typed() -> None:
    assert _roles(_normalized("python", "code-clean", "src")) == ("python", "code-clean", Path("src"))


def test_system_and_profiles_without_a_source_stay_as_typed() -> None:
    assert _roles(_normalized("python", "code-clean")) == ("python", "code-clean", None)


def test_system_and_a_folder_name_are_not_guessed() -> None:
    """`python src` is a system and a profile called 'src'; guessing would hide a typo."""
    assert _roles(_normalized("python", "src")) == ("python", "src", None)


# ---------------------------------------------------------------- the copy

def test_the_given_namespace_is_not_changed() -> None:
    args = build_parser().parse_args(["src"])
    result = normalize_positionals(args)
    assert (args.system, args.profiles, args.source) == ("src", None, None)
    assert result is not args


def test_everything_else_is_carried_over() -> None:
    args = _normalized("generic/all", "src", "-o", "out", "--format", "plain", "--no-tree", "--dry-run", "-vv")
    assert args.output == Path("out")
    assert args.format == "plain"
    assert args.add_tree is False
    assert args.dry_run is True
    assert args.verbose == 2


def test_the_result_is_a_namespace() -> None:
    assert isinstance(_normalized("src"), argparse.Namespace)
