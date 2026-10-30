from pathlib import Path
from simplibs.extractor.cli._helpers import describe_result
from simplibs.extractor.definitions import ExtractionConfig, ExtractionResult, FileReport


def _result(*statuses: str, **overrides) -> ExtractionResult:
    files = tuple(FileReport(Path(f"f{i}.txt"), f"f{i}.txt", status) for i, status in enumerate(statuses))
    values = {"config": ExtractionConfig(source=Path("project")), "profile_key": "python/code", "target": None, "files": files}
    values.update(overrides)
    return ExtractionResult(**values)


def test_a_fatal_run_names_its_reason() -> None:
    assert describe_result(_result(fatal="The source folder does not exist.")) == "python/code: The source folder does not exist."


def test_failed_files_are_counted() -> None:
    assert describe_result(_result("ok", "error", "error")) == "python/code: 2 file(s) failed"


def test_one_failed_file() -> None:
    assert describe_result(_result("error")) == "python/code: 1 file(s) failed"


def test_nothing_failed_means_nothing_was_selected() -> None:
    assert describe_result(_result()) == "python/code: no file was selected"
    assert describe_result(_result("skipped", "skipped")) == "python/code: no file was selected"


def test_the_fatal_reason_wins_over_failed_files() -> None:
    assert describe_result(_result("error", fatal="stopped")) == "python/code: stopped"


def test_the_line_starts_with_the_profile_key() -> None:
    assert describe_result(_result(profile_key="generic/all")).startswith("generic/all: ")
