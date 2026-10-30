from types import MappingProxyType
import pytest
from simplibs.extractor.logic.transform import steps_for


def test_no_steps_give_no_action() -> None:
    assert steps_for(None, ".py") is None
    assert steps_for(None, "") is None


def test_one_action_applies_to_every_suffix(make_action) -> None:
    action = make_action(str.upper)
    for suffix in [".py", ".md", ".PY", "", ".tar.gz"]:
        assert steps_for(action, suffix) is action


def test_mapping_picks_the_action_of_the_suffix(make_action) -> None:
    py, md = make_action(str.upper), make_action(str.lower)
    steps = {".py": py, ".md": md}
    assert steps_for(steps, ".py") is py
    assert steps_for(steps, ".md") is md


@pytest.mark.parametrize("suffix", [".py", ".PY", ".Py", ".pY"])
def test_suffix_case_is_ignored(make_action, suffix) -> None:
    py = make_action(str.upper)
    assert steps_for({".py": py}, suffix) is py


def test_unknown_suffix_without_a_fallback_gives_no_action(make_action) -> None:
    assert steps_for({".py": make_action(str.upper)}, ".txt") is None


def test_unknown_suffix_gets_the_fallback(make_action) -> None:
    py, fallback = make_action(str.upper), make_action(str.lower)
    steps = {".py": py, "*": fallback}
    assert steps_for(steps, ".txt") is fallback


def test_own_suffix_wins_over_the_fallback(make_action) -> None:
    py, fallback = make_action(str.upper), make_action(str.lower)
    assert steps_for({"*": fallback, ".py": py}, ".py") is py


def test_file_without_a_suffix_gets_the_fallback(make_action) -> None:
    fallback = make_action(str.lower)
    assert steps_for({".py": make_action(str.upper), "*": fallback}, "") is fallback


def test_fallback_alone_applies_to_everything(make_action) -> None:
    fallback = make_action(str.lower)
    for suffix in [".py", ".md", ""]:
        assert steps_for({"*": fallback}, suffix) is fallback


def test_empty_mapping_gives_no_action() -> None:
    assert steps_for({}, ".py") is None


def test_any_mapping_type_works(make_action) -> None:
    py = make_action(str.upper)
    assert steps_for(MappingProxyType({".py": py}), ".py") is py


def test_keys_are_matched_in_lowercase_only(make_action) -> None:
    """An uppercase key can never match: the lookup lowercases the suffix, not the keys (which is why Profile rejects them)."""
    assert steps_for({".PY": make_action(str.upper)}, ".py") is None
    assert steps_for({".PY": make_action(str.upper)}, ".PY") is None
