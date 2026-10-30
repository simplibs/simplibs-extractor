import argparse
import sys
from pathlib import Path
import pytest
from simplibs.exception import StateError
from simplibs.extractor.cli import collect_source
from simplibs.path import normalize_path

# `simplibs.extractor.cli.collect_source` is also the name of the function, so the MODULE is taken from `sys.modules`.
MODULE = sys.modules["simplibs.extractor.cli.collect_source"]


class PathPrompt:
    """A replacement for the question 'Source folder'; it records how it was asked."""

    def __init__(self, answer: Path | None = None) -> None:
        self.answer = answer
        self.questions: list[tuple[tuple, dict]] = []

    def __call__(self, *args, **kwargs):
        self.questions.append((args, kwargs))
        return self.answer


@pytest.fixture
def ask(monkeypatch):
    def _install(answer: Path | None) -> PathPrompt:
        fake = PathPrompt(answer)
        monkeypatch.setattr(MODULE, "prompt_path", fake)
        return fake

    return _install


def _args(source) -> argparse.Namespace:
    return argparse.Namespace(source=source)


# ---------------------------------------------------------------- a usable folder

def test_a_folder_is_returned_normalized(tmp_path) -> None:
    folder = tmp_path / "project"
    folder.mkdir()
    result = collect_source(_args(folder))
    assert result == normalize_path(folder)
    assert result.is_absolute()


def test_a_relative_folder_is_made_absolute(tmp_path, monkeypatch) -> None:
    (tmp_path / "project").mkdir()
    monkeypatch.chdir(tmp_path)
    assert collect_source(_args(Path("project"))) == normalize_path(tmp_path / "project")


def test_a_usable_folder_needs_no_terminal_and_no_question(tmp_path, ask) -> None:
    prompt = ask(None)
    collect_source(_args(tmp_path))
    assert prompt.questions == []


def test_a_usable_folder_is_not_asked_about_even_in_a_terminal(tmp_path, ask, terminals) -> None:
    terminals(stdin=True, stdout=True)
    prompt = ask(None)
    collect_source(_args(tmp_path))
    assert prompt.questions == []


# ---------------------------------------------------------------- nothing usable, nobody to ask

def test_a_missing_source_without_a_terminal_gives_a_state_card(ask) -> None:
    prompt = ask(None)
    with pytest.raises(StateError) as caught:
        collect_source(_args(None))
    assert caught.value.error_name == "CLI_NOT_INTERACTIVE"
    assert "the SOURCE folder is missing or is not a folder" in str(caught.value)
    assert prompt.questions == []


def test_a_path_that_does_not_exist_is_refused_without_a_terminal(tmp_path, ask) -> None:
    with pytest.raises(StateError):
        collect_source(_args(tmp_path / "nothing"))


def test_a_file_is_refused_without_a_terminal(tmp_path, ask) -> None:
    file = tmp_path / "a.txt"
    file.write_text("x\n", encoding="utf-8")
    with pytest.raises(StateError):
        collect_source(_args(file))


# ---------------------------------------------------------------- the question

def test_a_missing_source_is_asked_for_in_a_terminal(tmp_path, ask, terminals) -> None:
    terminals(stdin=True, stdout=True)
    answer = tmp_path / "chosen"
    answer.mkdir()
    prompt = ask(answer)

    assert collect_source(_args(None)) == normalize_path(answer)
    assert len(prompt.questions) == 1
    args, kwargs = prompt.questions[0]
    assert args == ("Source folder",)
    assert kwargs == {"kind": "dir", "must_exist": True}


@pytest.mark.parametrize("bad", ["missing", "a_file"])
def test_a_bad_source_is_replaced_by_the_answer_in_a_terminal(tmp_path, ask, terminals, bad) -> None:
    terminals(stdin=True, stdout=True)
    (tmp_path / "a_file").write_text("x\n", encoding="utf-8")
    answer = tmp_path / "chosen"
    answer.mkdir()
    prompt = ask(answer)

    assert collect_source(_args(tmp_path / bad)) == normalize_path(answer)
    assert len(prompt.questions) == 1


def test_a_terminal_for_output_only_is_not_enough(ask, terminals) -> None:
    terminals(stdin=False, stdout=True)
    with pytest.raises(StateError):
        collect_source(_args(None))
