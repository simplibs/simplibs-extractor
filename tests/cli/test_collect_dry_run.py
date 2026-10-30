import argparse
import sys
import pytest
from simplibs.extractor.cli import collect_dry_run

# `simplibs.extractor.cli.collect_dry_run` is also the name of the function, so the MODULE is taken from `sys.modules`.
MODULE = sys.modules["simplibs.extractor.cli.collect_dry_run"]


class Confirm:
    """A replacement for the yes/no question; it records how it was asked."""

    def __init__(self, answer: bool = True) -> None:
        self.answer = answer
        self.questions: list[tuple[tuple, dict]] = []

    def __call__(self, *args, **kwargs):
        self.questions.append((args, kwargs))
        return self.answer


@pytest.fixture
def confirm(monkeypatch) -> Confirm:
    fake = Confirm()
    monkeypatch.setattr(MODULE, "prompt_confirm", fake)
    return fake


def _args(dry_run) -> argparse.Namespace:
    return argparse.Namespace(dry_run=dry_run)


@pytest.mark.parametrize("asked", [False, True])
@pytest.mark.parametrize("flag", [True, False])
def test_the_flag_decides_and_nothing_is_asked(confirm, terminals, flag, asked) -> None:
    terminals(stdin=True, stdout=True)
    assert collect_dry_run(_args(flag), asked) is flag
    assert confirm.questions == []


def test_a_person_who_typed_everything_is_not_asked(confirm, terminals) -> None:
    terminals(stdin=True, stdout=True)
    assert collect_dry_run(_args(None), False) is False
    assert confirm.questions == []


@pytest.mark.parametrize("answer", [True, False])
def test_a_person_in_the_wizard_is_asked_and_the_answer_is_used(confirm, terminals, answer) -> None:
    terminals(stdin=True, stdout=True)
    confirm.answer = answer
    assert collect_dry_run(_args(None), True) is answer
    assert confirm.questions == [(("Dry run (write nothing)?",), {"default": False})]


@pytest.mark.parametrize("streams", [(False, False), (True, False), (False, True)])
def test_without_a_full_terminal_nothing_is_asked_and_the_run_is_real(confirm, terminals, streams) -> None:
    terminals(stdin=streams[0], stdout=streams[1])
    assert collect_dry_run(_args(None), True) is False
    assert confirm.questions == []
