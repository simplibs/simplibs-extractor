from pathlib import Path
import pytest
from simplibs.exception import ValidationError
from simplibs.extractor.definitions import ExtractionConfig, ExtractionResult, FileReport
from simplibs.extractor.logic.report import format_summary

SOURCE = Path("project")
TARGET = Path("project") / "extraction.md"
NOTHING_HINT = "  nothing to extract (check the source and the include/exclude rules)"


def _report(status: str, name: str, reason: str | None = None) -> FileReport:
    return FileReport(Path(name), name, status, reason)


def _result(*reports: FileReport, **overrides) -> ExtractionResult:
    values = {
        "config": ExtractionConfig(source=SOURCE),
        "profile_key": "generic/all",
        "target": TARGET,
        "written": True,
        "files": tuple(reports),
        "bytes_in": 100,
        "bytes_out": 90,
        "tokens_estimate": 23,
    }
    values.update(overrides)
    return ExtractionResult(**values)


# ---------------------------------------------------------------- a normal run

def test_a_successful_run_in_full() -> None:
    result = _result(
        _report("ok", "a.py"),
        _report("ok", "b.py"),
        _report("skipped", "logo.png", "not a text file"),
        _report("error", "broken.txt", "read failed: OSError: disk gone"),
        bytes_in=1_234_567,
        bytes_out=7_654,
        tokens_estimate=1_920,
    )
    assert format_summary(result).splitlines() == [
        "Extraction: generic/all",
        f"  source : {SOURCE}",
        f"  target : {TARGET} (written)",
        "  files  : 2 ok, 1 skipped, 1 errors",
        "  size   : 1,234,567 B in -> 7,654 B out (~1,920 tokens)",
        "  error  : broken.txt (read failed: OSError: disk gone)",
        "  skipped: logo.png (not a text file)",
    ]


def test_the_profile_key_is_in_the_first_line() -> None:
    assert format_summary(_result(_report("ok", "a.py"), profile_key="python/code-clean")).startswith(
        "Extraction: python/code-clean\n"
    )


def test_a_run_without_problems_lists_no_files() -> None:
    lines = format_summary(_result(_report("ok", "a.py"), _report("ok", "b.py"))).splitlines()
    assert len(lines) == 5
    assert "a.py" not in "\n".join(lines)


def test_there_is_no_trailing_line_break() -> None:
    assert not format_summary(_result(_report("ok", "a.py"))).endswith("\n")


@pytest.mark.parametrize(
    "overrides, state",
    [
        ({"written": True}, "written"),
        ({"written": False}, "not written"),
        ({"written": False, "dry_run": True}, "dry run, not written"),
        ({"written": True, "dry_run": True}, "dry run, not written"),
    ],
)
def test_the_state_of_the_output(overrides, state) -> None:
    assert f"  target : {TARGET} ({state})" in format_summary(_result(_report("ok", "a.py"), **overrides)).splitlines()


def test_small_numbers_have_no_separator() -> None:
    summary = format_summary(_result(_report("ok", "a.py"), bytes_in=12, bytes_out=9, tokens_estimate=3))
    assert "  size   : 12 B in -> 9 B out (~3 tokens)" in summary.splitlines()


# ---------------------------------------------------------------- files that need attention

def test_errors_are_listed_before_skipped_files_whatever_the_order_of_the_run() -> None:
    result = _result(
        _report("skipped", "s1.bin", "not a text file"),
        _report("ok", "a.py"),
        _report("error", "e1.txt", "read failed"),
        _report("skipped", "s2.bin", "too large"),
        _report("error", "e2.txt", "read failed"),
    )
    listed = [line for line in format_summary(result).splitlines() if line.startswith(("  error ", "  skipped"))]
    assert [line.split(":")[1].split(" (")[0].strip() for line in listed] == ["e1.txt", "e2.txt", "s1.bin", "s2.bin"]


def test_the_status_column_is_aligned() -> None:
    result = _result(_report("ok", "a.py"), _report("error", "e.txt", "x"), _report("skipped", "s.bin", "y"))
    lines = format_summary(result).splitlines()
    assert "  error  : e.txt (x)" in lines
    assert "  skipped: s.bin (y)" in lines


def test_at_most_ten_files_are_listed_by_default() -> None:
    result = _result(_report("ok", "a.py"), *[_report("error", f"e{i}.txt", "x") for i in range(15)])
    listed = [line for line in format_summary(result).splitlines() if line.startswith("  error  :")]
    assert len(listed) == 10
    assert "  files  : 1 ok, 0 skipped, 15 errors" in format_summary(result)    # the count still tells the truth


@pytest.mark.parametrize("max_listed, expected", [(0, 0), (1, 1), (3, 3), (50, 15)])
def test_max_listed_caps_the_list(max_listed, expected) -> None:
    result = _result(_report("ok", "a.py"), *[_report("error", f"e{i}.txt", "x") for i in range(15)])
    listed = [line for line in format_summary(result, max_listed=max_listed).splitlines() if line.startswith("  error  :")]
    assert len(listed) == expected


def test_the_cap_is_shared_by_errors_and_skipped_files_and_errors_use_it_first() -> None:
    result = _result(
        _report("ok", "a.py"),
        _report("error", "e1.txt", "x"),
        _report("error", "e2.txt", "x"),
        _report("skipped", "s1.bin", "y"),
        _report("skipped", "s2.bin", "y"),
    )
    lines = format_summary(result, max_listed=3).splitlines()
    assert [line for line in lines if "e1.txt" in line or "e2.txt" in line or "s1.bin" in line or "s2.bin" in line] == [
        "  error  : e1.txt (x)",
        "  error  : e2.txt (x)",
        "  skipped: s1.bin (y)",
    ]


# ---------------------------------------------------------------- nothing extracted

def test_an_empty_selection_gets_a_hint() -> None:
    lines = format_summary(_result()).splitlines()
    assert lines[-1] == NOTHING_HINT


def test_only_skipped_files_get_the_hint_after_the_list() -> None:
    lines = format_summary(_result(_report("skipped", "logo.png", "not a text file"))).splitlines()
    assert lines[-2] == "  skipped: logo.png (not a text file)"
    assert lines[-1] == NOTHING_HINT


def test_only_failed_files_get_the_hint_too() -> None:
    lines = format_summary(_result(_report("error", "e.txt", "x"))).splitlines()
    assert lines[-1] == NOTHING_HINT


def test_one_ok_file_means_no_hint() -> None:
    assert NOTHING_HINT not in format_summary(_result(_report("ok", "a.py"), _report("error", "e.txt", "x")))


# ---------------------------------------------------------------- a run that stopped early

def test_a_fatal_run_says_only_why() -> None:
    result = _result(_report("ok", "a.py"), fatal="The source folder does not exist.", written=False)
    assert format_summary(result).splitlines() == [
        "Extraction: generic/all",
        "  FAILED: The source folder does not exist.",
    ]


def test_a_fatal_run_hides_everything_else() -> None:
    result = _result(_report("error", "e.txt", "x"), fatal="stopped", target=None, written=False)
    summary = format_summary(result)
    assert "e.txt" not in summary
    assert "target" not in summary
    assert "size" not in summary


# ---------------------------------------------------------------- the arguments

def test_only_a_result_is_accepted() -> None:
    for value in (None, "result", 5, {"profile_key": "a/b"}):
        with pytest.raises(ValidationError):
            format_summary(value)


@pytest.mark.parametrize("max_listed", ["3", None, 1.5, [3]])
def test_max_listed_must_be_a_whole_number(max_listed) -> None:
    with pytest.raises(ValidationError):
        format_summary(_result(_report("ok", "a.py")), max_listed=max_listed)


def test_max_listed_is_keyword_only() -> None:
    with pytest.raises(TypeError):
        format_summary(_result(_report("ok", "a.py")), 3)  # type: ignore[misc]
