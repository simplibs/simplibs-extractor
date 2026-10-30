import pytest
import sys

from simplibs.extractor.cli import run_init
from simplibs.extractor.constants import DEFAULT_PROFILE_KEY, DEFAULT_SCRIPT_NAME


MODULE = sys.modules["simplibs.extractor.cli.run_init"]


def test_run_init_writes_the_script_and_returns_zero(tmp_path, capsys) -> None:
    """The folder gets the default script, and the output says where it is."""
    code = run_init([str(tmp_path), "--profile", "generic/all"])

    script = tmp_path / DEFAULT_SCRIPT_NAME
    out = capsys.readouterr().out
    assert code == 0
    assert script.is_file()
    assert "generic/all" in script.read_text(encoding="utf-8")
    assert "Created:" in out and DEFAULT_SCRIPT_NAME in out


def test_run_init_without_a_profile_and_without_a_terminal_uses_the_default(tmp_path) -> None:
    """Nobody to ask, so the default profile is written."""
    code = run_init([str(tmp_path)])

    assert code == 0
    assert DEFAULT_PROFILE_KEY in (tmp_path / DEFAULT_SCRIPT_NAME).read_text(encoding="utf-8")


def test_run_init_an_existing_script_is_refused_with_a_card_and_left_alone(tmp_path, capsys) -> None:
    """Return code 2, the card on standard error, nothing printed as success."""
    script = tmp_path / DEFAULT_SCRIPT_NAME
    script.write_text("# mine\n", encoding="utf-8")

    code = run_init([str(tmp_path), "--profile", "generic/all"])

    captured = capsys.readouterr()
    assert code == 2
    assert captured.err.strip() != ""
    assert "Created:" not in captured.out
    assert script.read_text(encoding="utf-8") == "# mine\n"


def test_run_init_force_replaces_an_existing_script(tmp_path) -> None:
    """`--force` is the way to overwrite."""
    script = tmp_path / DEFAULT_SCRIPT_NAME
    script.write_text("# mine\n", encoding="utf-8")

    code = run_init([str(tmp_path), "--profile", "generic/all", "--force"])

    assert code == 0
    assert script.read_text(encoding="utf-8") != "# mine\n"


def test_run_init_an_unknown_profile_is_refused_before_anything_is_written(tmp_path, capsys) -> None:
    """The profile is resolved first, so a typo leaves no half-made file."""
    code = run_init([str(tmp_path), "--profile", "generic/no-such-profile"])

    captured = capsys.readouterr()
    assert code == 2
    assert "EXTRACTOR_PROFILE_NOT_FOUND" in captured.err
    assert not (tmp_path / DEFAULT_SCRIPT_NAME).exists()


def test_run_init_a_script_name_without_py_is_refused(tmp_path, capsys) -> None:
    """A script that could not be run is not written."""
    code = run_init([str(tmp_path / "script.txt"), "--profile", "generic/all"])

    captured = capsys.readouterr()
    assert code == 2
    assert "EXTRACTOR_CONFIG_INVALID" in captured.err
    assert not (tmp_path / "script.txt").exists()


def test_run_init_a_script_file_name_is_used_as_given(tmp_path) -> None:
    """`init some/name.py` writes that file."""
    target = tmp_path / "my_extract.py"

    code = run_init([str(target), "--profile", "generic/all"])

    assert code == 0
    assert target.is_file()


def test_run_init_the_card_goes_to_standard_error_not_to_standard_output(tmp_path, capsys) -> None:
    """A piped result is never mixed with diagnostics."""
    run_init([str(tmp_path), "--profile", "generic/no-such-profile"])

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""


def test_run_init_a_syntax_error_of_the_arguments_exits_through_argparse() -> None:
    """Not a card: `argparse` prints its usage and exits with 2."""
    with pytest.raises(SystemExit) as raised:
        run_init(["--no-such-option"])

    assert raised.value.code == 2

def test_run_init_without_a_profile_and_with_a_terminal_asks_for_one(
    tmp_path, monkeypatch
) -> None:
    """The available profiles are offered and the chosen one is written."""
    calls = []

    monkeypatch.setattr(MODULE, "is_interactive", lambda: True)

    def choose(prompt, options, default):
        calls.append((prompt, options, default))
        return DEFAULT_PROFILE_KEY

    monkeypatch.setattr(MODULE, "prompt_choice", choose)

    code = run_init([str(tmp_path)])

    script = tmp_path / DEFAULT_SCRIPT_NAME

    assert code == 0
    assert len(calls) == 1

    prompt, options, default = calls[0]

    assert prompt == "Profile"
    assert DEFAULT_PROFILE_KEY in options
    assert default == DEFAULT_PROFILE_KEY
    assert DEFAULT_PROFILE_KEY in script.read_text(encoding="utf-8")