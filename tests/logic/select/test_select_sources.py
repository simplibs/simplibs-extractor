from pathlib import Path
from unittest.mock import MagicMock
import pytest
from simplibs.file import IGNORE_DRAFTS
from simplibs.path import DEFAULT_IGNORE_NAMES, normalize_path
from simplibs.rules import IsTyping, Rule
from simplibs.extractor.definitions import Profile
from simplibs.extractor.logic.select import resolve_config, select_sources

ALWAYS = IsTyping(Path)       # every relative path is a Path: always true
NEVER = ~IsTyping(Path)       # always false

PROJECT_FILES = {"a.py", "b.txt", "sub/c.py", "sub/deep/d.md"}


def _build(root: Path, with_housekeeping: bool = True) -> Path:
    """A small project; the folders git and Python leave behind are optional."""
    for name in PROJECT_FILES:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"text of {name}\n", encoding="utf-8")
    if with_housekeeping:
        (root / ".git").mkdir()
        (root / ".git" / "config").write_text("x\n", encoding="utf-8")
        (root / "__pycache__").mkdir()
        (root / "__pycache__" / "x.pyc").write_text("x\n", encoding="utf-8")
    return root


@pytest.fixture
def project(tmp_path) -> Path:
    root = tmp_path / "project"
    root.mkdir()
    return _build(root)


def _select(root: Path, **overrides) -> list[Path]:
    return select_sources(resolve_config(None, {"source": root, **overrides}))


def _relatives(root: Path, selected: list[Path]) -> set[str]:
    base = normalize_path(root)
    return {path.relative_to(base).as_posix() for path in selected}


@pytest.fixture
def needs_standard_ignores():
    """The housekeeping folders of the fixture are only ignored if the path library ignores them by default."""
    if not {".git", "__pycache__"} <= (DEFAULT_IGNORE_NAMES | IGNORE_DRAFTS):
        pytest.skip("'.git' and '__pycache__' are not in the default ignore names of simplibs-path")


# ---------------------------------------------------------------- what is collected

def test_every_text_file_of_the_project_is_selected(project, needs_standard_ignores) -> None:
    assert _relatives(project, _select(project)) == PROJECT_FILES


def test_paths_are_absolute(project, needs_standard_ignores) -> None:
    assert all(path.is_absolute() for path in _select(project))


def test_result_is_sorted(project, needs_standard_ignores) -> None:
    selected = _select(project)
    assert selected == sorted(selected)


def test_result_is_a_list_of_paths(project, needs_standard_ignores) -> None:
    selected = _select(project)
    assert isinstance(selected, list)
    assert all(isinstance(path, Path) for path in selected)


def test_an_empty_folder_selects_nothing(tmp_path) -> None:
    empty = tmp_path / "empty"
    empty.mkdir()
    assert _select(empty) == []


def test_recursive_false_takes_only_the_top_level(project, needs_standard_ignores) -> None:
    assert _relatives(project, _select(project, recursive=False)) == {"a.py", "b.txt"}


# ---------------------------------------------------------------- ignore names

def test_housekeeping_folders_are_skipped_by_default(project, needs_standard_ignores) -> None:
    relatives = _relatives(project, _select(project))
    assert not any(name.startswith((".git/", "__pycache__/")) for name in relatives)


def test_own_ignore_names_replace_the_default(project) -> None:
    """With a custom set the default is gone: `sub` is skipped, but `.git` and `__pycache__` are read."""
    relatives = _relatives(project, _select(project, ignore_names=frozenset({"sub"})))
    assert relatives == {"a.py", "b.txt", ".git/config", "__pycache__/x.pyc"}


def test_empty_ignore_names_skip_nothing(project) -> None:
    relatives = _relatives(project, _select(project, ignore_names=frozenset()))
    assert relatives == PROJECT_FILES | {".git/config", "__pycache__/x.pyc"}


def test_a_file_name_can_be_ignored_too(project, needs_standard_ignores) -> None:
    relatives = _relatives(project, _select(project, ignore_names=frozenset({"b.txt"})))
    assert "b.txt" not in relatives
    assert "a.py" in relatives


# ---------------------------------------------------------------- the output and skip_paths

def test_default_output_is_never_selected(project, needs_standard_ignores) -> None:
    (project / "extraction.md").write_text("old output\n", encoding="utf-8")
    assert "extraction.md" not in _relatives(project, _select(project))


def test_output_named_by_the_profile_is_never_selected(project, needs_standard_ignores) -> None:
    (project / "dump.txt").write_text("old output\n", encoding="utf-8")
    profile = Profile("python", "dump", output_name="dump.txt")
    relatives = _relatives(project, _select(project, profile=profile))
    assert "dump.txt" not in relatives


def test_given_target_inside_the_source_is_never_selected(project, needs_standard_ignores) -> None:
    (project / "sub" / "result.md").write_text("old output\n", encoding="utf-8")
    relatives = _relatives(project, _select(project, target=project / "sub" / "result.md"))
    assert "sub/result.md" not in relatives
    assert "sub/c.py" in relatives


def test_other_output_file_in_the_source_is_still_selected(project, needs_standard_ignores) -> None:
    """Only the file this run writes is banned; a different old extraction is just a text file."""
    (project / "extraction.md").write_text("old output\n", encoding="utf-8")
    relatives = _relatives(project, _select(project, target=project / "sub" / "result.md"))
    assert "extraction.md" in relatives


def test_target_outside_the_source_changes_nothing(project, tmp_path, needs_standard_ignores) -> None:
    relatives = _relatives(project, _select(project, target=tmp_path / "out.md"))
    assert relatives == PROJECT_FILES


@pytest.mark.parametrize("as_text", [False, True])
def test_skip_paths_are_never_selected(project, needs_standard_ignores, as_text) -> None:
    skipped = project / "sub" / "c.py"
    relatives = _relatives(project, _select(project, skip_paths=(str(skipped) if as_text else skipped,)))
    assert relatives == PROJECT_FILES - {"sub/c.py"}


def test_several_skip_paths(project, needs_standard_ignores) -> None:
    relatives = _relatives(project, _select(project, skip_paths=(project / "a.py", project / "b.txt")))
    assert relatives == PROJECT_FILES - {"a.py", "b.txt"}


def test_skip_path_that_does_not_exist_is_harmless(project, needs_standard_ignores) -> None:
    assert _relatives(project, _select(project, skip_paths=(project / "nothing.py",))) == PROJECT_FILES


# ---------------------------------------------------------------- the rules (wiring only: AND / OR)

@pytest.mark.parametrize(
    "overrides, expected_all",
    [
        ({}, True),                                   # no rules at all
        ({"include": ALWAYS}, True),
        ({"include": NEVER}, False),
        ({"exclude": ALWAYS}, False),
        ({"exclude": NEVER}, True),
        ({"include": ALWAYS, "exclude": NEVER}, True),
        ({"include": ALWAYS, "exclude": ALWAYS}, False),   # exclude wins over include
        ({"include": NEVER, "exclude": NEVER}, False),
    ],
)
def test_rules_of_the_config(project, needs_standard_ignores, overrides, expected_all) -> None:
    relatives = _relatives(project, _select(project, **overrides))
    assert relatives == (PROJECT_FILES if expected_all else set())


@pytest.mark.parametrize(
    "profile_include, config_include, expected_all",
    [
        (ALWAYS, ALWAYS, True),
        (ALWAYS, NEVER, False),    # the config can only narrow ...
        (NEVER, ALWAYS, False),    # ... and cannot widen what the profile took
        (NEVER, NEVER, False),
        (ALWAYS, None, True),
        (None, ALWAYS, True),
        (NEVER, None, False),
        (None, NEVER, False),
    ],
)
def test_include_of_profile_and_config_are_combined_by_and(
    project, needs_standard_ignores, profile_include, config_include, expected_all
) -> None:
    profile = Profile("t", "x", include=profile_include)
    relatives = _relatives(project, _select(project, profile=profile, include=config_include))
    assert relatives == (PROJECT_FILES if expected_all else set())


@pytest.mark.parametrize(
    "profile_exclude, config_exclude, expected_all",
    [
        (NEVER, NEVER, True),
        (ALWAYS, NEVER, False),    # either one is enough to drop a file
        (NEVER, ALWAYS, False),
        (ALWAYS, ALWAYS, False),
        (ALWAYS, None, False),
        (None, ALWAYS, False),
        (NEVER, None, True),
        (None, NEVER, True),
    ],
)
def test_exclude_of_profile_and_config_are_combined_by_or(
    project, needs_standard_ignores, profile_exclude, config_exclude, expected_all
) -> None:
    profile = Profile("t", "x", exclude=profile_exclude)
    relatives = _relatives(project, _select(project, profile=profile, exclude=config_exclude))
    assert relatives == (PROJECT_FILES if expected_all else set())


# ---------------------------------------------------------------- the rules see the relative path

def _spy() -> tuple[MagicMock, list]:
    """A rule that records what it is asked and passes everything."""
    seen: list = []
    rule = MagicMock(spec=Rule)
    rule.side_effect = lambda path: seen.append(path) or True
    return rule, seen


@pytest.mark.parametrize("parents", [(), ("tests",), ("a", "src", "tests")])
def test_include_rule_gets_the_path_relative_to_the_source(tmp_path, parents) -> None:
    """Where the project lies on the disk must not matter - a project inside a folder called `tests` is not dropped."""
    root = tmp_path.joinpath(*parents, "project")
    root.mkdir(parents=True)
    _build(root, with_housekeeping=False)
    rule, seen = _spy()

    selected = _select(root, profile=Profile("t", "x", include=rule))

    assert {Path(path).as_posix() for path in seen} == PROJECT_FILES
    assert all(not Path(path).is_absolute() for path in seen)
    assert _relatives(root, selected) == PROJECT_FILES


def test_exclude_rule_gets_the_path_relative_to_the_source(tmp_path) -> None:
    root = tmp_path / "tests" / "project"
    root.mkdir(parents=True)
    _build(root, with_housekeeping=False)
    rule, seen = _spy()
    rule.side_effect = lambda path: seen.append(path) or False

    selected = _select(root, profile=Profile("t", "x", exclude=rule))

    assert {Path(path).as_posix() for path in seen} == PROJECT_FILES
    assert _relatives(root, selected) == PROJECT_FILES


def test_the_output_and_skipped_files_are_not_shown_to_the_rules(tmp_path) -> None:
    """They are dropped before any rule runs."""
    root = tmp_path / "project"
    root.mkdir()
    _build(root, with_housekeeping=False)
    (root / "extraction.md").write_text("old\n", encoding="utf-8")
    rule, seen = _spy()

    _select(root, profile=Profile("t", "x", include=rule), skip_paths=(root / "a.py",))

    assert {Path(path).as_posix() for path in seen} == PROJECT_FILES - {"a.py"}


# ---------------------------------------------------------------- symbolic links

def _link(link: Path, target: Path) -> None:
    try:
        link.symlink_to(target)
    except (OSError, NotImplementedError):
        pytest.skip("symbolic links are not available here")


def _secret(tmp_path: Path) -> Path:
    secret = tmp_path / "outside" / "secret.txt"
    secret.parent.mkdir()
    secret.write_text("TOP SECRET\n", encoding="utf-8")
    return secret


def test_a_link_leading_outside_is_selected_under_its_own_name(project, tmp_path, needs_standard_ignores) -> None:
    """Whether its content may be read is decided by the read phase; the selection only names it."""
    _link(project / "link.txt", _secret(tmp_path))
    assert _relatives(project, _select(project)) == PROJECT_FILES | {"link.txt"}


def test_the_rules_see_a_link_by_its_own_name(tmp_path) -> None:
    root = tmp_path / "project"
    root.mkdir()
    _build(root, with_housekeeping=False)
    _link(root / "link.txt", _secret(tmp_path))
    rule, seen = _spy()

    _select(root, profile=Profile("t", "x", include=rule))

    assert {Path(path).as_posix() for path in seen} == PROJECT_FILES | {"link.txt"}
