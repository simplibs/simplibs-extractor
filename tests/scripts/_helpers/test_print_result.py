from pathlib import Path
import pytest
from simplibs.extractor.definitions import ExtractionConfig, ExtractionResult, FileReport
from simplibs.extractor.logic.report import format_summary
from simplibs.extractor.scripts._helpers import print_result


def _result(*statuses: str, **overrides) -> ExtractionResult:
    files = tuple(FileReport(Path(f"f{i}.txt"), f"f{i}.txt", status, None if status == "ok" else "why") for i, status in enumerate(statuses))
    values = {
        "config": ExtractionConfig(source=Path("project")),
        "profile_key": "generic/all",
        "target": Path("project") / "extraction.md",
        "written": True,
        "files": files,
        "bytes_in": 10,
        "bytes_out": 9,
        "tokens_estimate": 3,
    }
    values.update(overrides)
    return ExtractionResult(**values)


def test_a_successful_result_is_printed_as_its_summary(capsys) -> None:
    result = _result("ok", "ok")
    print_result(result)
    assert capsys.readouterr().out == format_summary(result) + "\n"


def test_a_failed_result_is_printed_as_its_summary(capsys) -> None:
    result = _result("ok", "error")
    print_result(result)
    assert capsys.readouterr().out == format_summary(result) + "\n"


def test_a_fatal_result_is_printed_as_its_summary(capsys) -> None:
    result = _result(fatal="The source folder does not exist.", written=False)
    print_result(result)
    assert capsys.readouterr().out == "Extraction: generic/all\n  FAILED: The source folder does not exist.\n"


def test_an_empty_run_is_printed_with_its_hint(capsys) -> None:
    print_result(_result())
    assert "nothing to extract" in capsys.readouterr().out


def test_it_prints_to_the_standard_output_only(capsys) -> None:
    print_result(_result("ok"))
    captured = capsys.readouterr()
    assert captured.out != ""
    assert captured.err == ""


def test_it_returns_nothing(capsys) -> None:
    assert print_result(_result("ok")) is None


def test_the_output_has_no_escape_codes_when_styles_are_off(capsys) -> None:
    """The conftest switches styling off, so the headline is plain text too."""
    print_result(_result("ok"))
    assert "\x1b" not in capsys.readouterr().out
