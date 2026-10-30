from pathlib import Path
import pytest
from simplibs.exception import NotFoundError, ParamError, ValidationError
from simplibs.extractor.constants import GENERATED_MARKER
from simplibs.extractor.definitions import ExtractionResult, Profile
from simplibs.extractor.registry import register_profile
from simplibs.extractor.scripts import extract_here
from simplibs.path import normalize_path


@pytest.fixture
def folder(tmp_path) -> Path:
    root = tmp_path / "project"
    root.mkdir()
    (root / "a.txt").write_text("hello from a\n", encoding="utf-8")
    (root / "b.py").write_text("x = 1\n", encoding="utf-8")
    (root / "run.py").write_text("# the script itself\n", encoding="utf-8")
    return root


class FakeLogger:
    def __init__(self) -> None:
        self.records: list[tuple[str, str]] = []

    def _add(self, level, message, args):
        self.records.append((level, message % args if args else message))

    def log_debug(self, message, *args):
        self._add("debug", message, args)

    def log_info(self, message, *args):
        self._add("info", message, args)

    def log_success(self, message, *args):
        self._add("success", message, args)

    def log_warning(self, message, *args):
        self._add("warning", message, args)


def _relatives(result: ExtractionResult) -> list[str]:
    return [report.relative for report in result.files]


# ---------------------------------------------------------------- a script as the anchor

def test_a_script_as_the_anchor_means_its_folder_without_the_script(folder) -> None:
    result = extract_here(folder / "run.py", quiet=True)

    assert result.success is True
    assert _relatives(result) == ["a.txt", "b.py"]
    assert result.config.source == normalize_path(folder)


def test_the_output_lies_next_to_the_script(folder) -> None:
    result = extract_here(folder / "run.py", quiet=True)

    assert result.target == normalize_path(folder) / "extraction.md"
    assert result.target.read_text(encoding="utf-8").splitlines()[0] == f"<!-- {GENERATED_MARKER} -->"


def test_the_script_is_not_in_the_output(folder) -> None:
    result = extract_here(folder / "run.py", quiet=True)
    assert "the script itself" not in result.target.read_text(encoding="utf-8")


def test_the_anchor_may_be_text(folder) -> None:
    assert extract_here(str(folder / "run.py"), quiet=True).success


# ---------------------------------------------------------------- a folder as the anchor

def test_a_folder_as_the_anchor_is_the_source_and_nothing_is_left_out(folder) -> None:
    result = extract_here(folder, quiet=True)
    assert _relatives(result) == ["a.txt", "b.py", "run.py"]
    assert result.config.source == normalize_path(folder)


def test_a_missing_anchor_is_taken_for_a_folder_that_does_not_exist(tmp_path) -> None:
    with pytest.raises(NotFoundError):
        extract_here(tmp_path / "nothing", quiet=True)


# ---------------------------------------------------------------- profile and output name

def test_the_default_profile_is_generic_all(folder) -> None:
    assert extract_here(folder / "run.py", quiet=True).profile_key == "generic/all"


def test_a_profile_key_is_used(folder) -> None:
    register_profile(Profile("t", "plain-one", format="plain"))
    result = extract_here(folder / "run.py", "t/plain-one", quiet=True)
    assert result.profile_key == "t/plain-one"
    assert "# FILE: a.txt" in result.target.read_text(encoding="utf-8")


def test_a_profile_object_is_used(folder) -> None:
    profile = Profile("t", "unregistered", output_name="dump.txt", format="plain")
    result = extract_here(folder / "run.py", profile=profile, quiet=True)
    assert result.profile_key == "t/unregistered"
    assert result.target == normalize_path(folder) / "dump.txt"


def test_the_output_name_of_the_profile_is_the_default(folder) -> None:
    register_profile(Profile("t", "dump", output_name="dump.txt"))
    assert extract_here(folder / "run.py", "t/dump", quiet=True).target.name == "dump.txt"


def test_an_own_output_name_wins_over_the_profile(folder) -> None:
    register_profile(Profile("t", "dump", output_name="dump.txt"))
    result = extract_here(folder / "run.py", "t/dump", output_name="mine.md", quiet=True)
    assert result.target == normalize_path(folder) / "mine.md"


@pytest.mark.parametrize("name", ["sub/out.md", "../out.md", "", "a/b/c.md"])
def test_an_output_name_that_is_a_path_is_refused_before_anything_is_written(folder, name) -> None:
    before = sorted(path.name for path in folder.iterdir())
    with pytest.raises(ParamError) as caught:
        extract_here(folder / "run.py", output_name=name, quiet=True)
    assert caught.value.error_name == "EXTRACTOR_CONFIG_INVALID"
    assert sorted(path.name for path in folder.iterdir()) == before


def test_an_unknown_profile_fails_first(folder, capsys) -> None:
    with pytest.raises(NotFoundError):
        extract_here(folder / "run.py", "python/nothing")
    assert capsys.readouterr().out == ""
    assert not (folder / "extraction.md").exists()


# ---------------------------------------------------------------- the overrides

def test_the_callers_values_win_over_the_derived_ones(folder, tmp_path) -> None:
    elsewhere = tmp_path / "elsewhere.md"
    result = extract_here(folder / "run.py", target=elsewhere, quiet=True)
    assert result.target == normalize_path(elsewhere)
    assert not (folder / "extraction.md").exists()


def test_other_fields_can_be_set(folder) -> None:
    result = extract_here(folder / "run.py", title="My code", format="plain", add_tree=True, quiet=True)
    text = result.target.read_text(encoding="utf-8")
    assert "# My code" in text
    assert "# TREE" in text


def test_a_dry_run_writes_nothing(folder) -> None:
    result = extract_here(folder / "run.py", dry_run=True, quiet=True)
    assert result.dry_run is True
    assert not result.target.exists()


def test_own_skip_paths_are_added_to_the_script(folder) -> None:
    result = extract_here(folder / "run.py", skip_paths=(folder / "b.py",), quiet=True)
    assert _relatives(result) == ["a.txt"]


def test_an_unknown_parameter_is_refused(folder) -> None:
    with pytest.raises(ParamError):
        extract_here(folder / "run.py", sourc="typo", quiet=True)


def test_a_wrong_type_is_refused(folder) -> None:
    with pytest.raises(ValidationError):
        extract_here(folder / "run.py", overwrite="force", quiet=True)


def test_the_options_are_keyword_only(folder) -> None:
    with pytest.raises(TypeError):
        extract_here(folder / "run.py", None, "out.md")  # type: ignore[misc]


# ---------------------------------------------------------------- what is printed

def test_by_default_the_summary_is_printed(folder, capsys) -> None:
    result = extract_here(folder / "run.py")
    printed = capsys.readouterr().out
    assert "Extraction: generic/all" in printed
    assert "2 ok" in printed
    assert str(result.target) in printed


def test_quiet_prints_nothing(folder, capsys) -> None:
    extract_here(folder / "run.py", quiet=True)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_a_run_that_finds_nothing_still_prints_its_hint(tmp_path, capsys) -> None:
    empty = tmp_path / "empty"
    empty.mkdir()
    result = extract_here(empty)
    assert result.success is False
    assert "nothing to extract" in capsys.readouterr().out


def test_the_logger_is_passed_to_the_run(folder) -> None:
    logger = FakeLogger()
    extract_here(folder / "run.py", logger=logger, quiet=True)
    assert ("info", "Selected 2 file(s)") in logger.records


def test_the_result_is_returned(folder) -> None:
    assert isinstance(extract_here(folder / "run.py", quiet=True), ExtractionResult)
