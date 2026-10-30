import importlib.metadata
import os
import runpy
import subprocess
import sys
from pathlib import Path
import pytest
import simplibs.extractor
from simplibs.extractor.cli import run_cli
from simplibs.extractor.constants import GENERATED_MARKER
from simplibs.extractor.definitions import Profile
from simplibs.extractor.registry import register_profile


@pytest.fixture
def root(tmp_path) -> Path:
    folder = tmp_path / "project"
    folder.mkdir()
    (folder / "a.txt").write_text("hello from a\n", encoding="utf-8")
    (folder / "b.py").write_text("x = 1\n", encoding="utf-8")
    return folder


# ---------------------------------------------------------------- a normal command

def test_a_command_with_all_the_words_extracts_and_exits_with_zero(root, capsys) -> None:
    assert run_cli(["generic/all", str(root)]) == 0

    output = root / "extraction.md"
    assert output.read_text(encoding="utf-8").splitlines()[0] == f"<!-- {GENERATED_MARKER} -->"
    assert "Extraction: generic/all" in capsys.readouterr().out


def test_system_profile_and_source_as_three_words(root) -> None:
    register_profile(Profile("t", "dump", output_name="dump.md"))
    assert run_cli(["t", "dump", str(root)]) == 0
    assert (root / "dump.md").is_file()


def test_quiet_prints_nothing_but_still_writes(root, capsys) -> None:
    assert run_cli(["generic/all", str(root), "-q"]) == 0
    assert capsys.readouterr().out == ""
    assert (root / "extraction.md").is_file()


def test_dry_run_writes_nothing(root, capsys) -> None:
    assert run_cli(["generic/all", str(root), "--dry-run"]) == 0
    assert not (root / "extraction.md").exists()
    assert "dry run, not written" in capsys.readouterr().out


def test_o_sends_the_output_to_another_folder(root, tmp_path) -> None:
    out = tmp_path / "out"
    assert run_cli(["generic/all", str(root), "-o", str(out)]) == 0
    assert (out / "extraction.md").is_file()
    assert not (root / "extraction.md").exists()


def test_format_and_tree_options(root) -> None:
    assert run_cli(["generic/all", str(root), "--format", "plain", "--no-tree"]) == 0
    text = (root / "extraction.md").read_text(encoding="utf-8")
    assert "# FILE: a.txt" in text
    assert "# TREE" not in text


def test_two_profiles_in_one_command_write_two_files(root) -> None:
    register_profile(Profile("t", "a", output_name="one.md"))
    register_profile(Profile("t", "b", output_name="two.md", format="plain"))
    assert run_cli(["t/a,t/b", str(root)]) == 0
    assert (root / "one.md").is_file()
    assert "# FILE: a.txt" in (root / "two.md").read_text(encoding="utf-8")


def test_running_again_gives_the_same_file(root) -> None:
    run_cli(["generic/all", str(root), "-q"])
    first = (root / "extraction.md").read_bytes()
    run_cli(["generic/all", str(root), "-q"])
    assert (root / "extraction.md").read_bytes() == first


# ---------------------------------------------------------------- exit code 1: it ran, but did not succeed

def test_an_empty_folder_exits_with_one_and_says_why(tmp_path, capsys) -> None:
    empty = tmp_path / "empty"
    empty.mkdir()

    assert run_cli(["generic/all", str(empty)]) == 1

    printed = capsys.readouterr().out
    assert "The following items failed:" in printed
    assert "generic/all: no file was selected" in printed
    assert not (empty / "extraction.md").exists()


def test_a_second_run_with_the_error_policy_exits_with_one_and_keeps_the_file(root, capsys) -> None:
    run_cli(["generic/all", str(root), "-q"])
    before = (root / "extraction.md").read_bytes()

    assert run_cli(["generic/all", str(root), "--overwrite", "error"]) == 1

    assert (root / "extraction.md").read_bytes() == before
    assert "FAILED" in capsys.readouterr().out


# ---------------------------------------------------------------- exit code 2: refused before anything ran

def test_an_unknown_profile_exits_with_two_and_names_it_on_standard_error(root, capsys) -> None:
    assert run_cli(["python/nothing", str(root)]) == 2
    captured = capsys.readouterr()
    assert "python/nothing" in captured.err
    assert not (root / "extraction.md").exists()


def test_a_source_that_is_not_a_folder_exits_with_two(root, capsys) -> None:
    assert run_cli(["generic/all", str(root / "a.txt")]) == 2
    assert "SOURCE" in capsys.readouterr().err


def test_a_missing_profile_without_a_terminal_exits_with_two(root, capsys) -> None:
    assert run_cli([str(root)]) == 2
    assert "no profile was given" in capsys.readouterr().err
    assert not (root / "extraction.md").exists()


def test_a_wrong_option_leaves_through_argparse() -> None:
    with pytest.raises(SystemExit) as caught:
        run_cli(["--nonsense"])
    assert caught.value.code == 2


# ---------------------------------------------------------------- questions

def test_list_systems(capsys) -> None:
    assert run_cli(["--list-systems"]) == 0
    printed = capsys.readouterr().out
    assert printed.startswith("Systems:")
    assert "generic" in printed


def test_list_profiles(capsys) -> None:
    assert run_cli(["--list-profiles", "generic"]) == 0
    assert "Profiles of generic:" in capsys.readouterr().out


# ---------------------------------------------------------------- add-ons

class _EntryPoint:
    def __init__(self, name, function) -> None:
        self.name = name
        self._function = function

    def load(self):
        return self._function


def test_a_profile_from_an_installed_add_on_is_usable_from_the_command_line(root, monkeypatch) -> None:
    def addon() -> None:
        register_profile(Profile("addon", "one", output_name="addon.md"))

    monkeypatch.setattr(importlib.metadata, "entry_points", lambda *, group: [_EntryPoint("addon", addon)])

    assert run_cli(["addon/one", str(root)]) == 0
    assert (root / "addon.md").is_file()


# ---------------------------------------------------------------- python -m simplibs.extractor

def test_the_module_runs_the_same_command(monkeypatch, capsys) -> None:
    monkeypatch.setattr(sys, "argv", ["simplibs-extractor", "--list-systems"])
    with pytest.raises(SystemExit) as caught:
        runpy.run_module("simplibs.extractor", run_name="__main__", alter_sys=True)
    assert caught.value.code == 0
    assert "Systems:" in capsys.readouterr().out


def test_the_command_runs_in_a_separate_process(root) -> None:
    """The real thing: a new interpreter, no test helpers, the exit code of the process."""
    source_folder = Path(simplibs.extractor.__file__).resolve().parents[2]
    environment = dict(os.environ)
    environment["PYTHONPATH"] = os.pathsep.join(filter(None, [str(source_folder), environment.get("PYTHONPATH", "")]))
    environment["NO_COLOR"] = "1"

    completed = subprocess.run(
        [sys.executable, "-m", "simplibs.extractor", "generic/all", str(root), "-q"],
        capture_output=True,
        text=True,
        env=environment,
        timeout=120,
        stdin=subprocess.DEVNULL,
    )

    assert completed.returncode == 0, completed.stderr
    assert (root / "extraction.md").is_file()
