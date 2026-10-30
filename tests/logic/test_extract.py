import logging
from pathlib import Path
import pytest
from simplibs.exception import AlreadyExistsError, NotFoundError, ParamError, ValidationError
from simplibs.extractor.constants import GENERATED_MARKER
from simplibs.extractor.definitions import ExtractionConfig, ExtractionResult, Profile
from simplibs.extractor.logic.report import estimate_tokens
from simplibs.extractor.logic import extract
from simplibs.extractor.registry import register_profile
from simplibs.path import normalize_path

FILES = {"a.py": "x = 1\n", "b.txt": "hello\n", "sub/c.md": "# Title\n"}


def _write(root: Path, name: str, content: str | bytes) -> Path:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content if isinstance(content, bytes) else content.encode("utf-8"))
    return path


@pytest.fixture
def root(tmp_path) -> Path:
    folder = tmp_path / "project"
    folder.mkdir()
    for name, content in FILES.items():
        _write(folder, name, content)
    return folder


def _output(result: ExtractionResult) -> str:
    return result.target.read_text(encoding="utf-8")


class FakeLogger:
    """A logger with the four `log_*` methods of SimpleLogger; keeps (level, formatted message)."""

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


# ---------------------------------------------------------------- a normal run

def test_a_normal_run_writes_the_output_and_succeeds(root) -> None:
    result = extract(source=root)

    assert isinstance(result, ExtractionResult)
    assert result.success is True
    assert result.written is True
    assert result.dry_run is False
    assert result.fatal is None
    assert result.profile_key == "generic/all"
    assert result.target == normalize_path(root) / "extraction.md"
    assert result.target.is_file()


def test_every_file_is_reported_in_path_order(root) -> None:
    result = extract(source=root)
    assert [report.relative for report in result.files] == ["a.py", "b.txt", "sub/c.md"]
    assert [report.status for report in result.files] == ["ok", "ok", "ok"]


def test_the_output_is_a_marked_markdown_document_with_every_file(root) -> None:
    result = extract(source=root)
    text = _output(result)
    assert text.splitlines()[0] == f"<!-- {GENERATED_MARKER} -->"
    for name, content in FILES.items():
        assert f"## `{name}`" in text
        assert content.rstrip("\n") in text
    assert text.index("## `a.py`") < text.index("## `b.txt`") < text.index("## `sub/c.md`")


def test_the_numbers_of_the_result_are_true(root) -> None:
    result = extract(source=root)
    written = result.target.read_bytes()
    assert result.bytes_in == sum(len(content.encode("utf-8")) for content in FILES.values())
    assert result.bytes_out == len(written)
    assert result.tokens_estimate == estimate_tokens(written.decode("utf-8"))
    assert result.tokens_estimate > 0
    assert isinstance(result.duration, float) and result.duration >= 0


def test_the_config_of_the_result_is_the_resolved_one(root) -> None:
    result = extract(source=str(root))
    assert result.config.source == normalize_path(root)
    assert result.config.target == result.target


def test_a_folder_name_with_spaces_and_diacritics(tmp_path) -> None:
    folder = tmp_path / "můj projekt"
    folder.mkdir()
    _write(folder, "a.txt", "Příliš žluťoučký kůň\n")
    result = extract(source=folder)
    assert result.success
    assert "Příliš žluťoučký kůň" in _output(result)
    assert "# Extraction: můj projekt" in _output(result)


def test_the_suffix_of_a_file_is_matched_in_lowercase(tmp_path) -> None:
    folder = tmp_path / "project"
    folder.mkdir()
    _write(folder, "Script.PY", "x = 1\n")
    assert "```python" in _output(extract(source=folder))


# ---------------------------------------------------------------- title, format, tree

def test_the_default_title_is_the_folder_name(root) -> None:
    assert "# Extraction: project" in _output(extract(source=root))


def test_a_chosen_title_is_written(root) -> None:
    assert "# My code" in _output(extract(source=root, title="My code"))


def test_plain_format(root) -> None:
    text = _output(extract(source=root, format="plain"))
    assert text.splitlines()[0] == f"# {GENERATED_MARKER}"
    assert "# FILE: a.py" in text
    assert "```" not in text


def test_the_tree_is_written_only_when_asked_for(root) -> None:
    assert "# TREE" in _output(extract(source=root, format="plain", add_tree=True))
    assert "# TREE" not in _output(extract(source=root, format="plain", add_tree=False))


def test_the_format_of_the_profile_is_used(root) -> None:
    register_profile(Profile("t", "plain-one", format="plain"))
    assert "# FILE: a.py" in _output(extract(source=root, profile="t/plain-one"))


# ---------------------------------------------------------------- running it again

def test_a_second_run_gives_the_same_output(root) -> None:
    """Deterministic, and the first output is not read as a source of the second."""
    first = extract(source=root)
    first_text = first.target.read_bytes()
    second = extract(source=root)
    assert second.target.read_bytes() == first_text
    assert [report.relative for report in second.files] == ["a.py", "b.txt", "sub/c.md"]


def test_an_old_output_under_another_name_is_skipped_not_extracted(root) -> None:
    extract(source=root, target=root / "old.md")
    second = extract(source=root, target=root / "new.md")

    skipped = {report.relative: report.reason for report in second.skipped_files}
    assert skipped == {"old.md": "generated by simplibs-extractor"}
    assert "old.md" not in _output(second)
    assert second.success is True


# ---------------------------------------------------------------- dry run

def test_a_dry_run_writes_nothing_but_reports_everything(root) -> None:
    result = extract(source=root, dry_run=True)

    assert not result.target.exists()
    assert result.written is False
    assert result.dry_run is True
    assert result.success is True
    assert len(result.ok_files) == 3
    assert result.bytes_out > 0
    assert result.tokens_estimate > 0
    assert sorted(path.name for path in root.iterdir()) == ["a.py", "b.txt", "sub"]


def test_a_dry_run_matches_the_real_run(root) -> None:
    planned = extract(source=root, dry_run=True)
    real = extract(source=root)
    assert planned.target == real.target
    assert planned.bytes_out == real.bytes_out
    assert planned.tokens_estimate == real.tokens_estimate
    assert planned.files == real.files


def test_a_dry_run_with_unique_names_the_file_it_would_write(root) -> None:
    extract(source=root)
    result = extract(source=root, dry_run=True, overwrite="unique")
    assert result.target.name == "extraction (1).md"
    assert not result.target.exists()


# ---------------------------------------------------------------- overwrite policies

def test_error_policy_refuses_an_existing_output(root) -> None:
    first = extract(source=root)
    before = first.target.read_bytes()
    with pytest.raises(AlreadyExistsError):
        extract(source=root, overwrite="error")
    assert first.target.read_bytes() == before


def test_unique_policy_keeps_the_old_output(root) -> None:
    first = extract(source=root)
    second = extract(source=root, overwrite="unique")
    assert second.target.name == "extraction (1).md"
    assert second.target.is_file() and first.target.is_file()


def test_backup_policy_keeps_a_copy_of_the_old_output(root) -> None:
    first = extract(source=root, title="First")
    result = extract(source=root, overwrite="backup", title="Second")
    others = [path for path in root.iterdir() if path.is_file() and path not in (first.target, root / "a.py", root / "b.txt")]
    assert "# Second" in _output(result)
    assert len(others) == 1
    assert "# First" in others[0].read_text(encoding="utf-8")


# ---------------------------------------------------------------- files that stay out

def test_a_binary_file_is_skipped(root) -> None:
    _write(root, "logo.png", b"\x89PNG\r\n\x1a\n\x00\x00\x00")
    result = extract(source=root)
    assert {report.relative: report.reason for report in result.skipped_files} == {"logo.png": "not a text file"}
    assert "logo.png" not in _output(result)
    assert result.success is True


def test_bytes_in_counts_only_the_files_that_went_in(root) -> None:
    _write(root, "logo.png", b"\x89PNG\r\n\x1a\n\x00\x00\x00" * 100)
    result = extract(source=root)
    assert result.bytes_in == sum(len(content.encode("utf-8")) for content in FILES.values())


def test_the_size_limit_skips_larger_files(root) -> None:
    result = extract(source=root, max_file_size=7)
    assert [report.relative for report in result.ok_files] == ["a.py", "b.txt"]
    assert [report.relative for report in result.skipped_files] == ["sub/c.md"]
    assert result.skipped_files[0].reason.startswith("too large")


def test_skip_paths_keep_a_file_out_of_the_selection(root) -> None:
    result = extract(source=root, skip_paths=(root / "b.txt",))
    assert [report.relative for report in result.files] == ["a.py", "sub/c.md"]


# ---------------------------------------------------------------- steps

def test_the_steps_of_the_profile_change_the_output(root, make_action) -> None:
    profile = Profile("t", "up", steps=make_action(str.upper))
    result = extract(source=root, profile=profile)
    text = _output(result)
    assert "HELLO" in text and "X = 1" in text
    assert result.ok_files[1].bytes_out == len("HELLO\n")


def test_a_step_that_fails_costs_only_its_own_file(root, make_action) -> None:
    def broken(text):
        raise RuntimeError("boom")

    profile = Profile("t", "bad", steps={".py": make_action(broken)})
    result = extract(source=root, profile=profile)

    assert [report.relative for report in result.error_files] == ["a.py"]
    assert result.error_files[0].reason == "transform failed: RuntimeError: boom"
    assert result.success is False
    assert result.written is True
    text = _output(result)
    assert "hello" in text and "# Title" in text
    assert "x = 1" not in text


# ---------------------------------------------------------------- nothing to write

def test_an_empty_folder_writes_nothing_and_fails(tmp_path) -> None:
    folder = tmp_path / "empty"
    folder.mkdir()
    result = extract(source=folder)

    assert result.success is False
    assert result.written is False
    assert result.files == ()
    assert result.bytes_out == 0
    assert result.tokens_estimate == 0
    assert result.target == normalize_path(folder) / "extraction.md"
    assert list(folder.iterdir()) == []


def test_a_folder_with_only_a_binary_file_writes_nothing(tmp_path) -> None:
    folder = tmp_path / "pics"
    folder.mkdir()
    _write(folder, "logo.png", b"\x89PNG\r\n\x1a\n\x00\x00\x00")
    result = extract(source=folder)
    assert result.success is False
    assert result.written is False
    assert [report.status for report in result.files] == ["skipped"]
    assert [path.name for path in folder.iterdir()] == ["logo.png"]


def test_when_every_file_fails_nothing_is_written(root, make_action) -> None:
    profile = Profile("t", "bad", steps=make_action(lambda text: 1 / 0))
    result = extract(source=root, profile=profile)
    assert result.success is False
    assert result.written is False
    assert len(result.error_files) == 3
    assert not result.target.exists()


def test_an_old_output_is_left_alone_when_there_is_nothing_new(tmp_path) -> None:
    folder = tmp_path / "empty"
    folder.mkdir()
    old = _write(folder, "extraction.md", "previous content\n")
    extract(source=folder)
    assert old.read_text(encoding="utf-8") == "previous content\n"


# ---------------------------------------------------------------- a configuration that cannot run

def test_an_unknown_parameter_fails_before_any_file_is_touched(root) -> None:
    before = sorted(path.name for path in root.iterdir())
    with pytest.raises(ParamError):
        extract(source=root, sourc="typo")
    assert sorted(path.name for path in root.iterdir()) == before


def test_a_missing_source_parameter(tmp_path) -> None:
    with pytest.raises(ParamError):
        extract(dry_run=True)


def test_a_missing_source_folder(tmp_path) -> None:
    with pytest.raises(NotFoundError):
        extract(source=tmp_path / "nothing")


def test_an_unknown_profile(root) -> None:
    with pytest.raises(NotFoundError):
        extract(source=root, profile="python/nothing")


def test_an_unknown_format(root) -> None:
    with pytest.raises(ParamError):
        extract(source=root, format="pdf")


def test_a_wrong_type_is_a_validation_error(root) -> None:
    with pytest.raises(ValidationError):
        extract(source=root, overwrite="force")


def test_the_logger_is_keyword_only(root) -> None:
    with pytest.raises(TypeError):
        extract(None, FakeLogger())  # type: ignore[misc]


# ---------------------------------------------------------------- a ready config and overrides

def test_a_ready_config_runs_as_it_is(root) -> None:
    result = extract(ExtractionConfig(source=root, title="From config"))
    assert "# From config" in _output(result)


def test_overrides_change_a_copy_of_the_ready_config(root) -> None:
    config = ExtractionConfig(source=root, title="From config")
    result = extract(config, dry_run=True, title="Overridden")
    assert result.dry_run is True
    assert result.config.title == "Overridden"
    assert config.dry_run is False
    assert config.title == "From config"


# ---------------------------------------------------------------- the logger

def test_a_simplibs_like_logger_gets_the_story_of_the_run(root) -> None:
    logger = FakeLogger()
    result = extract(source=root, logger=logger)

    assert ("info", f"Extracting {result.config.source} with profile generic/all") in logger.records
    assert ("info", "Selected 3 file(s)") in logger.records
    assert ("debug", "a.py: ok") in logger.records
    assert ("success", f"Done: {result.target}") in logger.records


def test_skipped_files_are_logged_with_their_reason(root) -> None:
    _write(root, "logo.png", b"\x89PNG\r\n\x1a\n\x00\x00\x00")
    logger = FakeLogger()
    extract(source=root, logger=logger)
    assert ("debug", "logo.png: skipped (not a text file)") in logger.records


def test_a_failed_file_is_a_warning_and_the_end_is_not_a_success(root, make_action) -> None:
    logger = FakeLogger()
    profile = Profile("t", "bad", steps={".py": make_action(lambda text: 1 / 0)})
    result = extract(source=root, profile=profile, logger=logger)

    assert any(level == "warning" and message.startswith("a.py: error (transform failed: ZeroDivisionError") for level, message in logger.records)
    assert ("warning", f"Done: {result.target}") in logger.records
    assert not any(level == "success" for level, _ in logger.records)


def test_an_empty_run_is_a_warning(tmp_path) -> None:
    folder = tmp_path / "empty"
    folder.mkdir()
    logger = FakeLogger()
    extract(source=folder, logger=logger)
    assert ("warning", "Nothing to extract - no file was written") in logger.records
    assert not any(level == "success" for level, _ in logger.records)


def test_a_standard_logger_works_too(root, caplog) -> None:
    logger = logging.getLogger("extractor-test-extract")
    with caplog.at_level(logging.DEBUG, logger="extractor-test-extract"):
        result = extract(source=root, logger=logger)
    messages = [record.getMessage() for record in caplog.records if record.name == "extractor-test-extract"]
    assert "Selected 3 file(s)" in messages
    assert f"Done: {result.target}" in messages


def test_no_logger_means_silence(root, capsys) -> None:
    extract(source=root)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""
