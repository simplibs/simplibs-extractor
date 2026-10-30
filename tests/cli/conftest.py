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


@pytest.fixture
def terminals(monkeypatch):
    """Replace standard input and output with fake streams that are (not) terminals."""

    class FakeStream:
        def __init__(self, is_tty):
            self._is_tty = is_tty

        def isatty(self):
            return self._is_tty

        def write(self, text):
            return len(text)

        def flush(self):
            pass

    def _set(*, stdin, stdout):
        monkeypatch.setattr("sys.stdin", FakeStream(stdin))
        monkeypatch.setattr("sys.stdout", FakeStream(stdout))

    return _set
