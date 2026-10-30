from pathlib import Path
import pytest
from simplibs.exception import AlreadyExistsError, StateError
from simplibs.exception.testing import assert_exception_function
from simplibs.extractor.logic.write import write_output

POLICIES = ["overwrite", "unique", "backup", "error"]


def _others(folder: Path, keep: Path) -> list[Path]:
    """Everything in the folder except one path."""
    return sorted(path for path in folder.iterdir() if path != keep)


# ---------------------------------------------------------------- a free target

@pytest.mark.parametrize("policy", POLICIES)
def test_a_free_target_is_written_under_every_policy(tmp_path, policy) -> None:
    target = tmp_path / "out.md"
    final = write_output(target, "hello\n", policy, False)
    assert final == target
    assert target.read_text(encoding="utf-8") == "hello\n"


@pytest.mark.parametrize("policy", POLICIES)
def test_nothing_else_is_left_in_the_folder(tmp_path, policy) -> None:
    """The atomic write leaves no draft behind, and a free target needs no backup."""
    target = tmp_path / "out.md"
    write_output(target, "hello\n", policy, False)
    assert sorted(path.name for path in tmp_path.iterdir()) == ["out.md"]


def test_the_text_is_written_exactly(tmp_path) -> None:
    target = tmp_path / "out.md"
    write_output(target, "Příliš žluťoučký kůň\nline 2\n", "overwrite", False)
    assert target.read_bytes() == "Příliš žluťoučký kůň\nline 2\n".encode("utf-8")


def test_an_empty_text_makes_an_empty_file(tmp_path) -> None:
    target = tmp_path / "out.md"
    write_output(target, "", "overwrite", False)
    assert target.read_bytes() == b""


def test_missing_folders_are_created(tmp_path) -> None:
    target = tmp_path / "a" / "b" / "out.md"
    final = write_output(target, "x\n", "overwrite", False)
    assert final == target
    assert target.read_text(encoding="utf-8") == "x\n"


def test_the_result_is_a_path(tmp_path) -> None:
    assert isinstance(write_output(tmp_path / "out.md", "x\n", "overwrite", False), Path)


# ---------------------------------------------------------------- overwrite

def test_overwrite_replaces_the_old_file(tmp_path) -> None:
    target = tmp_path / "out.md"
    target.write_text("old\n", encoding="utf-8")
    final = write_output(target, "new\n", "overwrite", False)
    assert final == target
    assert target.read_text(encoding="utf-8") == "new\n"
    assert _others(tmp_path, target) == []


# ---------------------------------------------------------------- unique

def test_unique_writes_a_numbered_copy_and_keeps_the_old_file(tmp_path) -> None:
    target = tmp_path / "out.md"
    target.write_text("old\n", encoding="utf-8")
    final = write_output(target, "new\n", "unique", False)
    assert final.name == "out (1).md"
    assert final.parent == target.parent.resolve() or final.parent == target.parent
    assert final.read_text(encoding="utf-8") == "new\n"
    assert target.read_text(encoding="utf-8") == "old\n"


def test_unique_counts_on(tmp_path) -> None:
    target = tmp_path / "out.md"
    target.write_text("old\n", encoding="utf-8")
    (tmp_path / "out (1).md").write_text("older\n", encoding="utf-8")
    final = write_output(target, "new\n", "unique", False)
    assert final.name == "out (2).md"
    assert (tmp_path / "out (1).md").read_text(encoding="utf-8") == "older\n"


def test_unique_on_a_free_target_keeps_the_name(tmp_path) -> None:
    final = write_output(tmp_path / "out.md", "x\n", "unique", False)
    assert final.name == "out.md"


# ---------------------------------------------------------------- backup

def test_backup_keeps_the_old_content_in_another_file(tmp_path) -> None:
    target = tmp_path / "out.md"
    target.write_text("old\n", encoding="utf-8")
    final = write_output(target, "new\n", "backup", False)
    assert final == target
    assert target.read_text(encoding="utf-8") == "new\n"
    others = _others(tmp_path, target)
    assert len(others) == 1
    assert others[0].read_text(encoding="utf-8") == "old\n"


# ---------------------------------------------------------------- error

def test_error_refuses_an_existing_target_and_leaves_it_alone(subtests, tmp_path) -> None:
    target = tmp_path / "out.md"
    target.write_text("old\n", encoding="utf-8")
    assert_exception_function(
        subtests,
        lambda path: write_output(path, "new\n", "error", False),
        invalid_params=(target,),
        valid_params=(tmp_path / "fresh.md",),
        exception_type=AlreadyExistsError,
        error_name="EXTRACTOR_TARGET_EXISTS",
        verbose=False,
    )
    assert target.read_text(encoding="utf-8") == "old\n"
    assert _others(tmp_path, target) == [tmp_path / "fresh.md"]


def test_error_refuses_in_a_dry_run_too(tmp_path) -> None:
    """A dry run must tell the truth: the real run would fail, so the dry run fails."""
    target = tmp_path / "out.md"
    target.write_text("old\n", encoding="utf-8")
    with pytest.raises(AlreadyExistsError):
        write_output(target, "new\n", "error", True)
    assert target.read_text(encoding="utf-8") == "old\n"


# ---------------------------------------------------------------- a folder as the target

@pytest.mark.parametrize("dry_run", [False, True])
@pytest.mark.parametrize("policy", POLICIES)
def test_a_folder_is_never_a_target(subtests, tmp_path, policy, dry_run) -> None:
    folder = tmp_path / "out.md"
    folder.mkdir()
    assert_exception_function(
        subtests,
        lambda path: write_output(path, "x\n", policy, dry_run),
        invalid_params=(folder,),
        exception_type=StateError,
        error_name="EXTRACTOR_TARGET_IS_DIR",
        verbose=False,
    )
    assert list(folder.iterdir()) == []


# ---------------------------------------------------------------- dry run

@pytest.mark.parametrize("policy", ["overwrite", "unique", "backup"])
def test_a_dry_run_on_a_free_target_writes_nothing(tmp_path, policy) -> None:
    target = tmp_path / "out.md"
    final = write_output(target, "x\n", policy, True)
    assert final == target
    assert not target.exists()
    assert list(tmp_path.iterdir()) == []


def test_a_dry_run_creates_no_folders(tmp_path) -> None:
    target = tmp_path / "a" / "b" / "out.md"
    write_output(target, "x\n", "overwrite", True)
    assert not (tmp_path / "a").exists()


@pytest.mark.parametrize("policy", ["overwrite", "backup"])
def test_a_dry_run_does_not_touch_an_existing_file(tmp_path, policy) -> None:
    target = tmp_path / "out.md"
    target.write_text("old\n", encoding="utf-8")
    final = write_output(target, "new\n", policy, True)
    assert final == target
    assert target.read_text(encoding="utf-8") == "old\n"
    assert _others(tmp_path, target) == []


def test_a_dry_run_with_unique_names_the_file_it_would_write(tmp_path) -> None:
    target = tmp_path / "out.md"
    target.write_text("old\n", encoding="utf-8")
    final = write_output(target, "new\n", "unique", True)
    assert final.name == "out (1).md"
    assert not final.exists()
    assert target.read_text(encoding="utf-8") == "old\n"
