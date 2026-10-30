from pathlib import Path
import pytest
from simplibs.extractor.definitions import ExtractionConfig
from simplibs.extractor.logic._helpers import build_title


def test_a_chosen_title_wins(tmp_path) -> None:
    config = ExtractionConfig(source=tmp_path / "project", title="My code")
    assert build_title(config) == "My code"


def test_without_a_title_the_name_of_the_source_folder_is_used(tmp_path) -> None:
    config = ExtractionConfig(source=tmp_path / "project")
    assert build_title(config) == "Extraction: project"


@pytest.mark.parametrize("name", ["můj projekt", "příliš-žluťoučký", "with space", "v1.2"])
def test_any_folder_name_is_used_as_it_is(tmp_path, name) -> None:
    assert build_title(ExtractionConfig(source=tmp_path / name)) == f"Extraction: {name}"


def test_an_empty_title_counts_as_no_title(tmp_path) -> None:
    config = ExtractionConfig(source=tmp_path / "project", title="")
    assert build_title(config) == "Extraction: project"


def test_a_filesystem_root_has_no_name_so_its_whole_path_is_used() -> None:
    root = Path(Path.cwd().anchor)
    assert build_title(ExtractionConfig(source=root)) == f"Extraction: {root}"


def test_only_the_last_part_of_the_path_is_used(tmp_path) -> None:
    title = build_title(ExtractionConfig(source=tmp_path / "a" / "b" / "project"))
    assert title == "Extraction: project"


def test_the_title_has_no_line_break(tmp_path) -> None:
    assert "\n" not in build_title(ExtractionConfig(source=tmp_path / "project"))
