from dataclasses import FrozenInstanceError
from pathlib import Path
import pytest
from simplibs.extractor.definitions import ExtractionConfig, ExtractionResult, FileReport


def _report(status: str, name: str = "a.txt") -> FileReport:
    return FileReport(Path(name), name, status)


def _result(*statuses: str, fatal: str | None = None) -> ExtractionResult:
    files = tuple(_report(status, f"f{index}.txt") for index, status in enumerate(statuses))
    config = ExtractionConfig(source=Path("project"))
    return ExtractionResult(config, "generic/all", Path("out.md"), files=files, fatal=fatal)


def test_result_defaults() -> None:
    """Only config, profile_key and target are required."""
    result = ExtractionResult(ExtractionConfig(source=Path("project")), "generic/all", None)
    assert result.target is None
    assert result.written is False
    assert result.dry_run is False
    assert result.files == ()
    assert (result.bytes_in, result.bytes_out, result.tokens_estimate) == (0, 0, 0)
    assert result.duration == 0.0
    assert result.fatal is None


def test_file_groups_split_the_reports_by_status() -> None:
    """ok_files / skipped_files / error_files each hold exactly their own reports, in order."""
    result = _result("ok", "skipped", "error", "ok", "skipped")
    assert [report.relative for report in result.ok_files] == ["f0.txt", "f3.txt"]
    assert [report.relative for report in result.skipped_files] == ["f1.txt", "f4.txt"]
    assert [report.relative for report in result.error_files] == ["f2.txt"]


def test_file_groups_are_tuples_that_cover_every_file() -> None:
    """The groups are tuples and together contain every report exactly once."""
    result = _result("ok", "skipped", "error")
    for group in (result.ok_files, result.skipped_files, result.error_files):
        assert isinstance(group, tuple)
    assert len(result.ok_files) + len(result.skipped_files) + len(result.error_files) == len(result.files)


def test_file_groups_are_empty_without_files() -> None:
    """An empty run has empty groups."""
    result = _result()
    assert result.ok_files == result.skipped_files == result.error_files == ()


@pytest.mark.parametrize(
    "statuses, fatal, expected",
    [
        (("ok",), None, True),
        (("ok", "ok"), None, True),
        (("ok", "skipped"), None, True),            # skipped files are fine
        (("ok", "error"), None, False),             # one failure fails the run
        (("error",), None, False),
        (("skipped",), None, False),                # nothing entered the output
        ((), None, False),                          # an empty selection is a failure
        (("ok",), "the run stopped", False),        # a fatal reason always wins
        ((), "the run stopped", False),
    ],
)
def test_success(statuses, fatal, expected) -> None:
    """Success needs no fatal reason, no failed file and at least one file in the output."""
    assert _result(*statuses, fatal=fatal).success is expected


def test_result_is_frozen() -> None:
    """A finished result cannot be changed."""
    with pytest.raises(FrozenInstanceError):
        _result("ok").written = True  # type: ignore[misc]


def test_result_uses_slots() -> None:
    """No per-instance __dict__."""
    assert not hasattr(_result("ok"), "__dict__")


# ---------------------------------------------------------------- partial files

def test_partial_files_hold_the_partial_reports_in_order() -> None:
    result = _result("ok", "partial", "skipped", "partial", "error")
    assert [report.relative for report in result.partial_files] == ["f1.txt", "f3.txt"]


def test_partial_files_are_a_tuple_and_empty_without_files() -> None:
    assert isinstance(_result("partial").partial_files, tuple)
    assert _result().partial_files == ()


def test_the_other_groups_do_not_hold_partial_files() -> None:
    result = _result("partial")
    assert result.ok_files == result.skipped_files == result.error_files == ()


def test_the_groups_together_cover_every_file_once() -> None:
    result = _result("ok", "partial", "skipped", "error", "partial")
    groups = (result.ok_files, result.partial_files, result.skipped_files, result.error_files)
    assert sum(len(group) for group in groups) == len(result.files)


@pytest.mark.parametrize(
    "statuses, fatal, expected",
    [
        (("partial",), None, True),                 # a partial file is in the output
        (("partial", "partial"), None, True),
        (("ok", "partial"), None, True),
        (("partial", "skipped"), None, True),
        (("partial", "error"), None, False),        # one failure still fails the run
        (("partial",), "the run stopped", False),   # a fatal reason always wins
    ],
)
def test_success_with_partial_files(statuses, fatal, expected) -> None:
    assert _result(*statuses, fatal=fatal).success is expected
