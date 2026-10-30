from dataclasses import FrozenInstanceError
from pathlib import Path
import pytest
from simplibs.extractor.definitions import FileReport


def test_file_report_defaults() -> None:
    """Only path, relative and status are required; the rest has neutral defaults."""
    report = FileReport(Path("a.txt"), "a.txt", "ok")
    assert report.reason is None
    assert report.bytes_in == 0
    assert report.bytes_out == 0


def test_file_report_positional_order() -> None:
    """The order is path, relative, status, reason, bytes_in, bytes_out (other code builds it positionally)."""
    report = FileReport(Path("a.txt"), "a.txt", "skipped", "too large", 10, 0)
    assert report.path == Path("a.txt")
    assert report.relative == "a.txt"
    assert report.status == "skipped"
    assert report.reason == "too large"
    assert (report.bytes_in, report.bytes_out) == (10, 0)


def test_file_report_is_frozen() -> None:
    """A finished report cannot be changed."""
    report = FileReport(Path("a.txt"), "a.txt", "ok")
    with pytest.raises(FrozenInstanceError):
        report.status = "error"  # type: ignore[misc]


def test_file_report_uses_slots() -> None:
    """No per-instance __dict__."""
    assert not hasattr(FileReport(Path("a.txt"), "a.txt", "ok"), "__dict__")
