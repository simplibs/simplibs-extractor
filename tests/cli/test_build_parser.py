import argparse
from pathlib import Path
import pytest
from simplibs.extractor.cli import build_parser
from simplibs.extractor.registry import register_renderer


def _parse(*argv: str) -> argparse.Namespace:
    return build_parser().parse_args(list(argv))


def test_it_builds_a_parser_for_the_program() -> None:
    parser = build_parser()
    assert isinstance(parser, argparse.ArgumentParser)
    assert parser.prog == "simplibs-extractor"


def test_every_call_builds_a_new_parser() -> None:
    assert build_parser() is not build_parser()


def test_the_defaults_of_a_bare_command() -> None:
    args = _parse()
    assert args.system is None
    assert args.profiles is None
    assert args.source is None
    assert args.output is None
    assert args.format is None
    assert args.overwrite == "overwrite"
    assert args.add_tree is True
    assert args.dry_run is None          # None = "not decided": the wizard may ask
    assert args.quiet is False
    assert args.verbose == 0
    assert args.no_color is False
    assert args.list_systems is False
    assert args.list_profiles is None


# ---------------------------------------------------------------- the three optional words

def test_three_words_fill_system_profiles_and_source_in_order() -> None:
    args = _parse("python", "code-clean", "src")
    assert (args.system, args.profiles) == ("python", "code-clean")
    assert args.source == Path("src")
    assert isinstance(args.source, Path)


def test_fewer_words_leave_the_rest_empty() -> None:
    args = _parse("python")
    assert (args.system, args.profiles, args.source) == ("python", None, None)
    args = _parse("python", "a,b")
    assert (args.system, args.profiles, args.source) == ("python", "a,b", None)


def test_a_fourth_word_is_refused() -> None:
    with pytest.raises(SystemExit) as caught:
        _parse("python", "code-clean", "src", "extra")
    assert caught.value.code == 2


def test_options_may_stand_before_the_words() -> None:
    args = _parse("--dry-run", "-o", "out", "python", "a", "src")
    assert args.dry_run is True
    assert args.output == Path("out")
    assert (args.system, args.profiles, args.source) == ("python", "a", Path("src"))


# ---------------------------------------------------------------- output options

@pytest.mark.parametrize("flag", ["-o", "--output"])
def test_output_is_a_path(flag) -> None:
    args = _parse(flag, "out/dir")
    assert args.output == Path("out/dir")
    assert isinstance(args.output, Path)


@pytest.mark.parametrize("name", ["markdown", "plain"])
def test_the_built_in_formats_are_accepted(name) -> None:
    assert _parse("--format", name).format == name


def test_an_unknown_format_is_refused() -> None:
    with pytest.raises(SystemExit) as caught:
        _parse("--format", "pdf")
    assert caught.value.code == 2


def test_a_format_registered_later_becomes_a_choice() -> None:
    """The choices are read when the parser is built, so add-ons loaded before it are included."""
    with pytest.raises(SystemExit):
        _parse("--format", "fancy")
    register_renderer("fancy", lambda entries, context: "fancy")
    assert _parse("--format", "fancy").format == "fancy"


@pytest.mark.parametrize("policy", ["overwrite", "unique", "backup", "error"])
def test_every_overwrite_policy_is_accepted(policy) -> None:
    assert _parse("--overwrite", policy).overwrite == policy


def test_an_unknown_overwrite_policy_is_refused() -> None:
    with pytest.raises(SystemExit) as caught:
        _parse("--overwrite", "force")
    assert caught.value.code == 2


def test_no_tree_switches_the_tree_off() -> None:
    assert _parse("--no-tree").add_tree is False


def test_dry_run_switches_it_on() -> None:
    assert _parse("--dry-run").dry_run is True


# ---------------------------------------------------------------- how much to say

def test_quiet_and_no_color() -> None:
    args = _parse("-q", "--no-color")
    assert args.quiet is True
    assert args.no_color is True
    assert _parse("--quiet").quiet is True


@pytest.mark.parametrize(
    "argv, expected",
    [(["-v"], 1), (["--verbose"], 1), (["-vv"], 2), (["-v", "-v"], 2), (["-vvv"], 3)],
)
def test_verbose_counts(argv, expected) -> None:
    assert _parse(*argv).verbose == expected


# ---------------------------------------------------------------- questions

def test_list_systems() -> None:
    assert _parse("--list-systems").list_systems is True


def test_list_profiles_takes_a_system() -> None:
    assert _parse("--list-profiles", "python").list_profiles == "python"


def test_list_profiles_needs_a_system() -> None:
    with pytest.raises(SystemExit) as caught:
        _parse("--list-profiles")
    assert caught.value.code == 2


# ---------------------------------------------------------------- refusals and help

def test_an_unknown_option_is_refused() -> None:
    with pytest.raises(SystemExit) as caught:
        _parse("--nonsense")
    assert caught.value.code == 2


def test_help_mentions_the_program_and_the_init_command(capsys) -> None:
    with pytest.raises(SystemExit) as caught:
        _parse("--help")
    assert caught.value.code == 0
    printed = capsys.readouterr().out
    assert "simplibs-extractor" in printed
    assert "init" in printed
