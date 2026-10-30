import sys
from pathlib import Path
import pytest
from simplibs.extractor.cli import run_cli
from simplibs.extractor.constants import DEFAULT_SCRIPT_NAME
from simplibs.extractor.definitions import ExtractionResult, FileReport

# `simplibs.extractor.cli.run_cli` is also the name of the function, so the MODULE is taken from `sys.modules`.
MODULE = sys.modules["simplibs.extractor.cli.run_cli"]

OK_FILE = FileReport(Path("a.txt"), "a.txt", "ok", None, 1, 1)
BAD_FILE = FileReport(Path("b.txt"), "b.txt", "error", "read failed: OSError: gone")


def _result(config, **changes) -> ExtractionResult:
    values = {"config": config, "profile_key": "generic/all", "target": None, "files": (OK_FILE,)}
    values.update(changes)
    return ExtractionResult(**values)


@pytest.fixture
def source(tmp_path) -> Path:
    folder = tmp_path / "src"
    folder.mkdir()
    (folder / "a.txt").write_text("hello\n", encoding="utf-8")
    return folder


@pytest.fixture
def fake_extract_many(monkeypatch):
    """Replace the extraction by a fake that records what it was given and returns what the test sets."""

    class Fake:
        def __init__(self):
            self.calls: list[list] = []
            self.make = lambda config: _result(config)

        def __call__(self, configs, **kwargs):
            self.calls.append(list(configs))
            return [self.make(config) for config in configs]

    fake = Fake()
    monkeypatch.setattr(MODULE, "extract_many", fake)
    return fake


# ----------------------------------------------------------------------
# 0 — everything succeeded
# ----------------------------------------------------------------------

def test_run_cli_returns_zero_when_every_extraction_succeeded(source, fake_extract_many, capsys) -> None:
    """Nothing to report: the failure list stays silent."""
    code = run_cli(["generic/all", str(source), "-q"])

    captured = capsys.readouterr()
    assert code == 0
    assert captured.out == ""
    assert len(fake_extract_many.calls) == 1
    assert len(fake_extract_many.calls[0]) == 1


def test_run_cli_hands_over_one_config_per_profile_key_pointing_at_the_source(source, fake_extract_many) -> None:
    """The refused-before-running checks pass and the configs are built from the arguments."""
    run_cli(["generic/all", str(source), "-q"])

    config = fake_extract_many.calls[0][0]
    assert Path(config.source) == source
    assert config.profile == "generic/all"
    assert Path(config.target).parent == source


def test_run_cli_a_dry_run_flag_reaches_the_config(source, fake_extract_many) -> None:
    """The flag is decided before the first extraction runs."""
    run_cli(["generic/all", str(source), "-q", "--dry-run"])

    assert fake_extract_many.calls[0][0].dry_run is True


def test_run_cli_a_list_command_returns_zero_and_runs_nothing(fake_extract_many, capsys) -> None:
    """`--list-systems` is an answer, not an extraction."""
    code = run_cli(["--list-systems"])

    assert code == 0
    assert "generic" in capsys.readouterr().out
    assert fake_extract_many.calls == []


def test_run_cli_a_broken_add_on_does_not_stop_the_command(monkeypatch, capsys) -> None:
    """A plug-in that failed to load is a warning, not a failure of the command."""
    monkeypatch.setattr(MODULE, "load_plugins", lambda: ({}, {"broken-addon": "boom"}))

    assert run_cli(["--list-systems"]) == 0


# ----------------------------------------------------------------------
# 1 — some extraction failed or selected nothing
# ----------------------------------------------------------------------

@pytest.mark.parametrize(
    "changes, expected_line",
    [
        ({"fatal": "NotFoundError: The source is gone"}, "generic/all: NotFoundError: The source is gone"),
        ({"files": (OK_FILE, BAD_FILE)}, "generic/all: 1 file(s) failed"),
        ({"files": ()}, "generic/all: no file was selected"),
    ],
    ids=["fatal", "failed-files", "nothing-selected"],
)
def test_run_cli_returns_one_and_names_every_failed_extraction(source, fake_extract_many, capsys, changes, expected_line) -> None:
    """The failures are listed once more at the end, one line each."""
    fake_extract_many.make = lambda config: _result(config, **changes)

    code = run_cli(["generic/all", str(source), "-q"])

    out = capsys.readouterr().out
    assert code == 1
    assert "The following items failed:" in out
    assert expected_line in out


def test_run_cli_a_bug_inside_the_extraction_is_not_turned_into_an_exit_code(source, monkeypatch) -> None:
    """Only the library's own cards are handled; a RuntimeError comes out with its traceback."""

    def explode(configs, **kwargs):
        raise RuntimeError("a bug")

    monkeypatch.setattr(MODULE, "extract_many", explode)

    with pytest.raises(RuntimeError):
        run_cli(["generic/all", str(source), "-q"])


# ----------------------------------------------------------------------
# 2 — refused before anything ran
# ----------------------------------------------------------------------

def test_run_cli_without_arguments_and_without_a_terminal_is_refused(fake_extract_many, capsys) -> None:
    """Nobody can be asked, so a card says what is missing instead of the command waiting forever."""
    code = run_cli([])

    captured = capsys.readouterr()
    assert code == 2
    assert "CLI_NOT_INTERACTIVE" in captured.err
    assert fake_extract_many.calls == []


def test_run_cli_a_source_that_is_not_a_folder_is_refused(tmp_path, fake_extract_many, capsys) -> None:
    """Without a terminal there is no question to replace the bad value."""
    code = run_cli(["generic/all", str(tmp_path / "missing")])

    captured = capsys.readouterr()
    assert code == 2
    assert "CLI_NOT_INTERACTIVE" in captured.err
    assert fake_extract_many.calls == []


def test_run_cli_an_unknown_profile_is_refused_before_the_first_run(source, fake_extract_many, capsys) -> None:
    """The key is resolved while the configs are built."""
    code = run_cli(["generic/no-such-profile", str(source)])

    captured = capsys.readouterr()
    assert code == 2
    assert "EXTRACTOR_PROFILE_NOT_FOUND" in captured.err
    assert fake_extract_many.calls == []


def test_run_cli_an_output_that_is_a_file_is_refused(source, tmp_path, fake_extract_many, capsys) -> None:
    """`-o` takes a folder."""
    target = tmp_path / "taken.txt"
    target.write_text("x", encoding="utf-8")

    code = run_cli(["generic/all", str(source), "-o", str(target)])

    captured = capsys.readouterr()
    assert code == 2
    assert "EXTRACTOR_CONFIG_INVALID" in captured.err
    assert fake_extract_many.calls == []


def test_run_cli_two_profiles_writing_the_same_file_are_refused(source, fake_extract_many, capsys) -> None:
    """They would overwrite each other."""
    code = run_cli(["generic/all,generic/all", str(source)])

    captured = capsys.readouterr()
    assert code == 2
    assert "EXTRACTOR_CONFIG_INVALID" in captured.err
    assert fake_extract_many.calls == []


def test_run_cli_a_list_of_profiles_of_an_unknown_system_is_refused(fake_extract_many, capsys) -> None:
    """An unknown system is an error, not an empty list."""
    code = run_cli(["--list-profiles", "no-such-system"])

    captured = capsys.readouterr()
    assert code == 2
    assert "EXTRACTOR_CONFIG_INVALID" in captured.err
    assert fake_extract_many.calls == []


def test_run_cli_a_refusal_goes_to_standard_error_and_leaves_standard_output_clean(source, fake_extract_many, capsys) -> None:
    """A piped result is never mixed with diagnostics."""
    run_cli(["generic/no-such-profile", str(source)])

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""


def test_run_cli_a_syntax_error_of_the_arguments_exits_through_argparse() -> None:
    """Not a card: `argparse` prints its usage and exits with 2."""
    with pytest.raises(SystemExit) as raised:
        run_cli(["--no-such-option"])

    assert raised.value.code == 2


def test_run_cli_prints_each_result_when_not_quiet(source, fake_extract_many, monkeypatch) -> None:
    """Every extraction result is presented in the normal output mode."""
    printed = []
    monkeypatch.setattr(MODULE, "print_result", printed.append)

    code = run_cli(["generic/all", str(source)])

    assert code == 0
    assert len(printed) == 1
    assert printed[0].success is True

# ----------------------------------------------------------------------
# The `init` subcommand
# ----------------------------------------------------------------------

def test_run_cli_init_hands_over_to_run_init(tmp_path, fake_extract_many) -> None:
    """`init` has its own parser and writes the script instead of extracting."""
    code = run_cli(["init", str(tmp_path), "--profile", "generic/all"])

    assert code == 0
    assert (tmp_path / DEFAULT_SCRIPT_NAME).is_file()
    assert fake_extract_many.calls == []


def test_run_cli_init_passes_its_refusal_on_as_two(tmp_path) -> None:
    """An unknown profile makes `init` return 2 through `run_cli` too."""
    assert run_cli(["init", str(tmp_path), "--profile", "generic/no-such-profile"]) == 2
