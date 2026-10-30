import pytest
from simplibs.file import IGNORE_DRAFTS
from simplibs.path import DEFAULT_IGNORE_NAMES
from simplibs.extractor.logic.select import resolve_ignore_names


def test_none_gives_the_default_names_plus_drafts() -> None:
    assert resolve_ignore_names(None) == DEFAULT_IGNORE_NAMES | IGNORE_DRAFTS


def test_default_contains_both_parts() -> None:
    names = resolve_ignore_names(None)
    assert DEFAULT_IGNORE_NAMES <= names
    assert IGNORE_DRAFTS <= names


def test_default_is_a_set_of_names() -> None:
    names = resolve_ignore_names(None)
    assert isinstance(names, (set, frozenset))
    assert all(isinstance(name, str) for name in names)


def test_a_choice_replaces_the_default_completely() -> None:
    chosen = frozenset({"build"})
    assert resolve_ignore_names(chosen) is chosen
    assert resolve_ignore_names(chosen) == frozenset({"build"})


def test_an_empty_choice_means_ignore_nothing() -> None:
    """An empty set is a real choice (falsy, but not None) - it must not fall back to the default."""
    assert resolve_ignore_names(frozenset()) == frozenset()
