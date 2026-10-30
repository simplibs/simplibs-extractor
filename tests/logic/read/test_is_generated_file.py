import sys
from pathlib import Path
import pytest
from simplibs.exception import SimpleException
from simplibs.extractor.constants import GENERATED_MARKER, MARKER_SCAN_LINES
from simplibs.extractor.logic.read import is_generated_file

# `simplibs.extractor.logic.read.is_generated_file` is also the name of the function, so the MODULE is taken from `sys.modules`.
MODULE = sys.modules["simplibs.extractor.logic.read.is_generated_file"]


def _write(tmp_path: Path, data: bytes, name: str = "a.txt") -> Path:
    path = tmp_path / name
    path.write_bytes(data)
    return path


def _text(*lines: str) -> bytes:
    return ("\n".join(lines) + "\n").encode("utf-8")


# ---------------------------------------------------------------- where the marker may stand

@pytest.mark.parametrize(
    "line",
    [
        GENERATED_MARKER,
        f"<!-- {GENERATED_MARKER} -->",               # the markdown form
        f"# {GENERATED_MARKER}",                      # the plain form
        f"text before {GENERATED_MARKER} text after",
        f"    {GENERATED_MARKER}",
    ],
)
def test_marker_in_any_comment_form_is_recognized(tmp_path, line) -> None:
    """The marker is a plain substring; the comment syntax around it depends on the format."""
    assert is_generated_file(_write(tmp_path, _text(line, "body"))) is True


def test_marker_on_the_first_line(tmp_path) -> None:
    assert is_generated_file(_write(tmp_path, _text(GENERATED_MARKER, "x", "y", "z", "w"))) is True


def test_marker_on_the_last_scanned_line(tmp_path) -> None:
    lines = ["filler"] * (MARKER_SCAN_LINES - 1) + [GENERATED_MARKER]
    assert is_generated_file(_write(tmp_path, _text(*lines))) is True


def test_marker_one_line_too_late_is_not_seen(tmp_path) -> None:
    """Only the head is read, so a file that merely quotes the marker further down is an ordinary file."""
    lines = ["filler"] * MARKER_SCAN_LINES + [GENERATED_MARKER]
    assert is_generated_file(_write(tmp_path, _text(*lines))) is False


def test_text_without_the_marker(tmp_path) -> None:
    assert is_generated_file(_write(tmp_path, _text("hello", "world"))) is False


def test_partial_marker_is_not_a_marker(tmp_path) -> None:
    assert is_generated_file(_write(tmp_path, _text(GENERATED_MARKER[:-3]))) is False


def test_empty_file(tmp_path) -> None:
    assert is_generated_file(_write(tmp_path, b"")) is False


def test_file_without_a_final_newline(tmp_path) -> None:
    assert is_generated_file(_write(tmp_path, GENERATED_MARKER.encode("utf-8"))) is True


# ---------------------------------------------------------------- how the bytes look

def test_windows_line_endings(tmp_path) -> None:
    data = f"first\r\nsecond\r\n<!-- {GENERATED_MARKER} -->\r\n".encode("utf-8")
    assert is_generated_file(_write(tmp_path, data)) is True


def test_marker_after_a_byte_order_mark(tmp_path) -> None:
    data = ("\ufeff" + f"<!-- {GENERATED_MARKER} -->\n").encode("utf-8")
    assert is_generated_file(_write(tmp_path, data)) is True


def test_undecodable_bytes_never_raise(tmp_path) -> None:
    """Bad bytes become replacement characters; the marker on another line is still found."""
    data = b"\xff\xfe\x00 broken \x80\x81\n" + f"{GENERATED_MARKER}\n".encode("utf-8")
    assert is_generated_file(_write(tmp_path, data)) is True


def test_undecodable_bytes_without_a_marker_are_just_false(tmp_path) -> None:
    assert is_generated_file(_write(tmp_path, b"\xff\xfe\x00 broken \x80\x81\n")) is False


def test_diacritics_around_the_marker(tmp_path) -> None:
    assert is_generated_file(_write(tmp_path, _text(f"Příliš žluťoučký kůň {GENERATED_MARKER} úpěl"))) is True


def test_a_huge_file_is_checked_by_its_head(tmp_path) -> None:
    """The marker far below the head is never reached (and the whole file is never read into memory)."""
    path = tmp_path / "huge.txt"
    with path.open("w", encoding="utf-8") as handle:
        for _ in range(200_000):
            handle.write("a line of ordinary text\n")
        handle.write(GENERATED_MARKER + "\n")
    assert is_generated_file(path) is False


# ---------------------------------------------------------------- how the file is read

def test_only_the_scanned_lines_are_pulled_and_the_stream_is_closed(monkeypatch) -> None:
    pulled: list[str] = []
    closed: list[bool] = []

    def fake_iter_lines(path, **kwargs):
        try:
            for index in range(MARKER_SCAN_LINES + 50):
                pulled.append(f"line {index}")
                yield f"line {index}\n"
        finally:
            closed.append(True)

    monkeypatch.setattr(MODULE, "iter_lines", fake_iter_lines)

    assert is_generated_file(Path("whatever.txt")) is False
    assert len(pulled) == MARKER_SCAN_LINES
    assert closed == [True]


def test_stream_is_closed_even_when_the_marker_is_found(monkeypatch) -> None:
    closed: list[bool] = []

    def fake_iter_lines(path, **kwargs):
        try:
            yield f"{GENERATED_MARKER}\n"
            yield "more\n"
        finally:
            closed.append(True)

    monkeypatch.setattr(MODULE, "iter_lines", fake_iter_lines)

    assert is_generated_file(Path("whatever.txt")) is True
    assert closed == [True]


def test_bad_bytes_are_replaced_not_raised(monkeypatch) -> None:
    """The file is opened in the lenient mode, so a damaged head can never stop a run."""
    seen: dict = {}

    def fake_iter_lines(path, **kwargs):
        seen.update(kwargs)
        yield "x\n"

    monkeypatch.setattr(MODULE, "iter_lines", fake_iter_lines)

    is_generated_file(Path("whatever.txt"))
    assert seen.get("errors") == "replace"


def test_missing_file_is_not_hidden(tmp_path) -> None:
    """The function does not swallow a missing file; `read_source` checks the file before it asks."""
    with pytest.raises((SimpleException, OSError)):
        is_generated_file(tmp_path / "missing.txt")
