import os
from pathlib import Path
import pytest
from simplibs.exception import SimpleException
from simplibs.extractor.constants import GENERATED_MARKER, MARKER_SCAN_LINES
from simplibs.extractor.definitions import ExtractionConfig
from simplibs.extractor.logic import extract, extract_many


def _write(root: Path, name: str, content: str | bytes) -> Path:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content if isinstance(content, bytes) else content.encode("utf-8"))
    return path


@pytest.fixture
def root(tmp_path) -> Path:
    folder = tmp_path / "project"
    folder.mkdir()
    return folder


def _output(result) -> str:
    return result.target.read_text(encoding="utf-8")


def _symlink(link: Path, target: Path) -> None:
    try:
        link.symlink_to(target)
    except (OSError, NotImplementedError):
        pytest.skip("symbolic links are not available here")


# ---------------------------------------------------------------- how a file is encoded

def test_a_byte_order_mark_does_not_end_up_in_the_output(root) -> None:
    _write(root, "a.txt", b"\xef\xbb\xbfx = 1\n")
    result = extract(source=root)
    assert result.ok_files[0].relative == "a.txt"
    assert "x = 1" in _output(result)
    assert "\ufeff" not in _output(result)


def test_windows_line_endings_come_out_as_plain_line_breaks(root) -> None:
    _write(root, "a.txt", b"first\r\nsecond\r\n")
    result = extract(source=root)
    assert "first\nsecond" in _output(result)
    assert "\r" not in _output(result)


def test_the_output_is_the_same_whatever_the_line_endings_of_the_sources(tmp_path) -> None:
    unix, windows = tmp_path / "unix", tmp_path / "windows"
    for folder, data in [(unix, b"one\ntwo\n"), (windows, b"one\r\ntwo\r\n")]:
        folder.mkdir()
        _write(folder, "a.txt", data)
    first = extract(source=unix, title="Same")
    second = extract(source=windows, title="Same")
    assert first.target.read_bytes() == second.target.read_bytes()


def test_a_text_file_in_another_encoding_is_skipped_not_fatal(root) -> None:
    _write(root, "latin.txt", "café\n".encode("latin-1"))
    _write(root, "ok.txt", "plain\n")
    result = extract(source=root)
    assert [report.relative for report in result.ok_files] == ["ok.txt"]
    assert {report.relative: report.status for report in result.skipped_files} == {"latin.txt": "skipped"}
    assert result.fatal is None


def test_a_utf_16_file_is_skipped_with_the_default_reading(root) -> None:
    _write(root, "wide.txt", "hello\n".encode("utf-16"))
    _write(root, "ok.txt", "plain\n")
    result = extract(source=root)
    assert [report.relative for report in result.skipped_files] == ["wide.txt"]


def test_diacritics_and_symbols_in_the_text_survive(root) -> None:
    text = "Příliš žluťoučký kůň úpěl ďábelské ódy — ✓ 😀\n"
    _write(root, "a.txt", text)
    assert text.rstrip("\n") in _output(extract(source=root))


# ---------------------------------------------------------------- how a file is named

def test_unusual_file_names_are_kept_in_headings_and_in_the_tree(root) -> None:
    names = ["příliš žluťoučký.py", "a (1).txt", "[x].md", "sub dir/kůň.txt", "UPPER.TXT"]
    for name in names:
        _write(root, name, "x\n")
    result = extract(source=root, format="plain", add_tree=True)
    text = _output(result)
    for name in names:
        assert f"# FILE: {name}" in text
    assert len(result.ok_files) == len(names)


def test_many_files_keep_one_stable_order(root) -> None:
    for number in range(120):
        _write(root, f"dir{number % 7}/file{number:03d}.txt", f"{number}\n")
    first = extract(source=root)
    second = extract(source=root)
    assert [report.relative for report in first.files] == [report.relative for report in second.files]
    assert len(first.ok_files) == 120
    assert first.target.read_bytes() == second.target.read_bytes()


def test_an_empty_file_is_part_of_the_run_and_shown_as_empty(root) -> None:
    _write(root, "a.txt", "x\n")
    _write(root, "empty.txt", "")
    result = extract(source=root)
    assert [report.relative for report in result.ok_files] == ["a.txt", "empty.txt"]
    assert "(empty file)" in _output(result)


# ---------------------------------------------------------------- the marker

def test_a_user_file_that_mentions_the_marker_below_the_head_is_still_extracted(root) -> None:
    lines = ["filler"] * MARKER_SCAN_LINES + [f"mentions {GENERATED_MARKER} here"]
    _write(root, "notes.txt", "\n".join(lines) + "\n")
    result = extract(source=root)
    assert [report.relative for report in result.ok_files] == ["notes.txt"]


def test_a_file_that_starts_with_the_marker_is_taken_for_an_old_output(root) -> None:
    """The documented price of the marker: whatever starts with it is never extracted."""
    _write(root, "old.txt", f"# {GENERATED_MARKER}\nbody\n")
    _write(root, "ok.txt", "x\n")
    result = extract(source=root)
    assert [report.relative for report in result.skipped_files] == ["old.txt"]
    assert [report.relative for report in result.ok_files] == ["ok.txt"]


# ---------------------------------------------------------------- what is never written

def test_the_output_never_shows_where_the_project_lies_on_the_disk(root) -> None:
    _write(root, "a.txt", "x\n")
    for format_name in ["markdown", "plain"]:
        text = _output(extract(source=root, format=format_name, add_tree=True))
        assert str(root.parent) not in text
        assert str(root) not in text


# ---------------------------------------------------------------- symbolic links

def test_a_link_to_a_file_outside_never_leaks_its_location(root, tmp_path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    secret = _write(outside, "secret.txt", "TOP SECRET\n")
    _write(root, "a.txt", "x\n")
    _symlink(root / "link.txt", secret)

    result = extract(source=root)

    assert result.fatal is None
    assert {report.relative: report.reason for report in result.skipped_files} == {"link.txt": "points outside the source"}
    assert [report.relative for report in result.ok_files] == ["a.txt"]
    assert "TOP SECRET" not in _output(result)
    assert str(outside) not in _output(result)
    assert result.success is True


def test_a_link_that_stays_inside_the_source_is_extracted(root) -> None:
    _write(root, "real.txt", "real content\n")
    _symlink(root / "link.txt", root / "real.txt")

    result = extract(source=root)

    assert [report.relative for report in result.ok_files] == ["link.txt", "real.txt"]
    assert result.fatal is None


def test_a_broken_link_does_not_stop_the_run(root, tmp_path) -> None:
    _write(root, "a.txt", "x\n")
    _symlink(root / "dangling.txt", tmp_path / "does-not-exist.txt")

    result = extract(source=root)

    assert result.fatal is None
    assert "a.txt" in [report.relative for report in result.ok_files]


# ---------------------------------------------------------------- a target that cannot be written

def test_a_target_below_a_file_fails_with_a_card_and_hurts_nothing(root, tmp_path) -> None:
    _write(root, "a.txt", "x\n")
    blocker = _write(tmp_path, "blocker", "I am a file, not a folder\n")

    with pytest.raises((SimpleException, OSError)):
        extract(source=root, target=blocker / "out.md")

    assert blocker.read_text(encoding="utf-8") == "I am a file, not a folder\n"
    assert (root / "a.txt").read_text(encoding="utf-8") == "x\n"


def test_extract_many_turns_an_unwritable_target_into_a_failed_result(root, tmp_path) -> None:
    _write(root, "a.txt", "x\n")
    blocker = _write(tmp_path, "blocker", "I am a file, not a folder\n")
    good = tmp_path / "good.md"

    results = extract_many(
        [
            ExtractionConfig(source=root, target=blocker / "out.md"),
            ExtractionConfig(source=root, target=good),
        ]
    )

    assert [result.success for result in results] == [False, True]
    assert results[0].fatal
    assert good.is_file()


def test_a_read_only_source_file_is_still_extracted(root) -> None:
    path = _write(root, "a.txt", "x\n")
    os.chmod(path, 0o444)
    try:
        assert extract(source=root).ok_files[0].relative == "a.txt"
    finally:
        os.chmod(path, 0o644)
