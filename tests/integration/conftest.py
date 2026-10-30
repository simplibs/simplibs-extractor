import pytest


@pytest.fixture(autouse=True)
def no_terminal(monkeypatch):
    """Standard input is never a terminal here, so no command stops to ask a question (even under `pytest -s`)."""

    class _NotATerminal:
        def isatty(self):
            return False

        def read(self, *args):
            return ""

        def readline(self, *args):
            return ""

    monkeypatch.setattr("sys.stdin", _NotATerminal())
