import pytest
from simplibs.exception import SimpleError, ValidationError
from simplibs.extractor.definitions import Profile
from simplibs.extractor.logic.transform import apply_steps, by_suffix


def test_gives_the_same_step_to_every_suffix(make_action) -> None:
    step = make_action(str.upper)
    mapping = by_suffix(step, (".js", ".tsx"))
    assert mapping == {".js": step, ".tsx": step}
    assert mapping[".js"] is mapping[".tsx"]


def test_keeps_the_order_of_the_suffixes(make_action) -> None:
    mapping = by_suffix(make_action(str.upper), (".b", ".a", ".c"))
    assert list(mapping) == [".b", ".a", ".c"]


def test_a_list_is_accepted_too(make_action) -> None:
    step = make_action(str.upper)
    assert by_suffix(step, [".js", ".ts"]) == {".js": step, ".ts": step}


def test_no_suffixes_give_an_empty_mapping(make_action) -> None:
    assert by_suffix(make_action(str.upper), ()) == {}


def test_every_call_gives_a_new_mapping(make_action) -> None:
    step = make_action(str.upper)
    suffixes = (".js",)
    first, second = by_suffix(step, suffixes), by_suffix(step, suffixes)
    assert first == second
    assert first is not second


def test_the_mapping_is_a_usable_value_of_steps(make_action) -> None:
    step = make_action(str.upper)
    mapping = by_suffix(step, (".js", ".mjs"))
    assert apply_steps("ab", mapping, ".mjs") == "AB"
    assert apply_steps("ab", mapping, ".py") == "ab"


def test_a_profile_accepts_the_mapping(make_action) -> None:
    profile = Profile("t", "js", steps=by_suffix(make_action(str.upper), (".js", ".mjs")))
    assert set(profile.steps) == {".js", ".mjs"}


def test_a_key_that_is_not_a_suffix_is_refused_when_the_profile_is_built(make_action) -> None:
    """`by_suffix` does not judge the keys; the profile does, once, with its own name."""
    with pytest.raises(SimpleError):
        Profile("t", "bad", steps=by_suffix(make_action(str.upper), ("js",)))


@pytest.mark.parametrize("step", ["not an action", None, 5, str.upper])
def test_the_step_must_be_an_action(step) -> None:
    with pytest.raises(ValidationError):
        by_suffix(step, (".js",))


@pytest.mark.parametrize("suffixes", [None, 5, [".js", 5], [None]])
def test_the_suffixes_must_be_texts_in_a_sequence(make_action, suffixes) -> None:
    with pytest.raises(ValidationError):
        by_suffix(make_action(str.upper), suffixes)
