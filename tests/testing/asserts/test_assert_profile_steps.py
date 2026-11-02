import pytest
from simplibs.extractor.definitions import Profile
from simplibs.extractor.testing.asserts import assert_profile_steps


def test_correct_cases_pass(recorder, make_profile) -> None:
    assert_profile_steps(
        recorder,
        make_profile(),
        {".py": [("ab", "AB"), ("x = 1", "X = 1")]},
    )
    assert recorder.failed == {}
    assert recorder.passed == ["test_steps_.py_#index_0", "test_steps_.py_#index_1"]


def test_works_with_the_real_subtests_fixture(subtests, make_profile) -> None:
    assert_profile_steps(subtests, make_profile(), {".py": [("ab", "AB")]}, unchanged_suffixes=())


def test_nothing_to_check_opens_no_subtests(recorder, make_profile) -> None:
    assert_profile_steps(recorder, make_profile(), {})
    assert recorder.names == []


def test_a_wrong_expected_text_fails_with_the_text_the_steps_gave(recorder, make_profile) -> None:
    assert_profile_steps(recorder, make_profile(), {".py": [("ab", "ab")]})
    assert list(recorder.failed) == ["test_steps_.py_#index_0"]
    message = recorder.failed["test_steps_.py_#index_0"]
    assert "'.py'" in message
    assert "'ab'" in message
    assert "'AB'" in message


def test_the_fallback_step_serves_a_suffix_no_key_names(recorder, make_profile) -> None:
    assert_profile_steps(recorder, make_profile(), {".xyz": [("  a  ", "a")]})
    assert recorder.failed == {}


def test_the_suffix_decides_which_step_is_used(recorder, make_profile) -> None:
    assert_profile_steps(recorder, make_profile(), {".py": [("  a  ", "  A  ")], ".md": [("  a  ", "a")]})
    assert recorder.failed == {}


def test_one_action_for_every_suffix(recorder, make_action) -> None:
    profile = Profile("generic", "upper", description="Upper", steps=make_action(str.upper, name="Upper"))
    assert_profile_steps(recorder, profile, {".py": [("a", "A")], ".md": [("b", "B")]})
    assert recorder.failed == {}


def test_a_profile_without_steps_keeps_the_text(recorder) -> None:
    profile = Profile("generic", "all", description="Everything")
    assert_profile_steps(recorder, profile, {".py": [("a  b", "a  b")]}, unchanged_suffixes=(".py2", ".md"))
    assert recorder.failed == {}


def test_a_profile_without_steps_fails_a_case_that_expects_a_change(recorder) -> None:
    profile = Profile("generic", "all", description="Everything")
    assert_profile_steps(recorder, profile, {".py": [("a", "A")]})
    assert list(recorder.failed) == ["test_steps_.py_#index_0"]


def test_every_case_is_reported_on_its_own(recorder, make_profile) -> None:
    assert_profile_steps(recorder, make_profile(), {".py": [("a", "A"), ("b", "b"), ("c", "C")]})
    assert list(recorder.failed) == ["test_steps_.py_#index_1"]
    assert recorder.passed == ["test_steps_.py_#index_0", "test_steps_.py_#index_2"]


# ---------------------------------------------------------------- suffixes without a step

def test_a_suffix_without_any_step_passes(recorder, make_profile) -> None:
    profile = make_profile(steps={".py": make_profile().steps[".py"]})
    assert_profile_steps(recorder, profile, {}, unchanged_suffixes=(".md", ".txt"))
    assert recorder.failed == {}
    assert recorder.passed == ["test_no_step_#index_0_.md", "test_no_step_#index_1_.txt"]


def test_a_suffix_that_has_a_step_fails_and_names_the_step(recorder, make_profile) -> None:
    assert_profile_steps(recorder, make_profile(), {}, unchanged_suffixes=(".md",))
    assert list(recorder.failed) == ["test_no_step_#index_0_.md"]
    message = recorder.failed["test_no_step_#index_0_.md"]
    assert "'.md'" in message
    assert "Strip" in message


def test_a_step_that_changes_nothing_is_still_a_step(recorder, make_action) -> None:
    """The text would stay the same, but the choice of a step is what `unchanged_suffixes` asks about."""
    profile = Profile("generic", "noop", description="No-op", steps={".py": make_action(lambda text: text, name="Noop")})
    assert_profile_steps(recorder, profile, {".py": [("a", "a")]}, unchanged_suffixes=())
    assert_profile_steps(recorder, profile, {}, unchanged_suffixes=(".py",))
    assert list(recorder.failed) == ["test_no_step_#index_0_.py"]


# ---------------------------------------------------------------- cover_all_suffixes

@pytest.fixture
def two_suffix_profile(make_action) -> Profile:
    return Profile(
        "generic",
        "two",
        description="Two suffixes",
        steps={".py": make_action(str.upper, name="Upper"), ".js": make_action(str.lower, name="Lower")},
    )


def test_coverage_is_not_asked_by_default(recorder, two_suffix_profile) -> None:
    assert_profile_steps(recorder, two_suffix_profile, {".py": [("a", "A")]})
    assert recorder.failed == {}
    assert "test_every_suffix_has_a_case" not in recorder.names


def test_coverage_passes_when_every_suffix_has_a_case(recorder, two_suffix_profile) -> None:
    assert_profile_steps(
        recorder,
        two_suffix_profile,
        {".py": [("a", "A")], ".js": [("B", "b")]},
        cover_all_suffixes=True,
    )
    assert recorder.failed == {}
    assert recorder.passed[-1] == "test_every_suffix_has_a_case"


def test_coverage_names_the_suffixes_without_a_case(recorder, two_suffix_profile) -> None:
    assert_profile_steps(recorder, two_suffix_profile, {".py": [("a", "A")]}, cover_all_suffixes=True)
    assert list(recorder.failed) == ["test_every_suffix_has_a_case"]
    assert "['.js']" in recorder.failed["test_every_suffix_has_a_case"]


def test_coverage_needs_a_case_for_the_fallback(recorder, make_profile) -> None:
    """`.py` has its own key; the fallback `*` is reached only by a suffix that no key names."""
    assert_profile_steps(recorder, make_profile(), {".py": [("a", "A")]}, cover_all_suffixes=True)
    assert list(recorder.failed) == ["test_every_suffix_has_a_case"]
    assert "fallback" in recorder.failed["test_every_suffix_has_a_case"]


def test_coverage_is_complete_with_a_case_for_the_fallback(recorder, make_profile) -> None:
    assert_profile_steps(recorder, make_profile(), {".py": [("a", "A")], ".xyz": [(" a ", "a")]}, cover_all_suffixes=True)
    assert recorder.failed == {}


def test_a_suffix_without_a_step_does_not_count_as_a_case(recorder, two_suffix_profile) -> None:
    assert_profile_steps(
        recorder,
        two_suffix_profile,
        {".py": [("a", "A")]},
        unchanged_suffixes=(".md",),
        cover_all_suffixes=True,
    )
    assert list(recorder.failed) == ["test_every_suffix_has_a_case"]


@pytest.mark.parametrize("steps_kind", ["none", "one-action"])
def test_coverage_has_nothing_to_ask_when_the_steps_are_no_mapping(recorder, make_action, steps_kind) -> None:
    steps = None if steps_kind == "none" else make_action(str.upper, name="Upper")
    profile = Profile("generic", "x", description="X", steps=steps)
    assert_profile_steps(recorder, profile, {}, cover_all_suffixes=True)
    assert recorder.names == []


# ---------------------------------------------------------------- mistakes of the test itself

@pytest.mark.parametrize("suffix", ["*", ".PY", "py", "", "."], ids=["star", "upper", "no-dot", "empty", "dot-only"])
def test_a_suffix_that_is_not_a_file_suffix_in_cases_is_refused_at_once(recorder, make_profile, suffix) -> None:
    with pytest.raises(AssertionError, match="file suffixes"):
        assert_profile_steps(recorder, make_profile(), {suffix: [("a", "A")]})
    assert recorder.names == []


@pytest.mark.parametrize("suffix", ["*", ".PY", "py", ""], ids=["star", "upper", "no-dot", "empty"])
def test_a_suffix_that_is_not_a_file_suffix_in_unchanged_is_refused_at_once(recorder, make_profile, suffix) -> None:
    with pytest.raises(AssertionError, match="file suffixes"):
        assert_profile_steps(recorder, make_profile(), {}, unchanged_suffixes=(suffix,))
    assert recorder.names == []


def test_a_suffix_with_cases_and_without_a_step_is_refused_at_once(recorder, make_profile) -> None:
    with pytest.raises(AssertionError, match="also unchanged"):
        assert_profile_steps(recorder, make_profile(), {".md": [("a", "a")]}, unchanged_suffixes=(".md",))
    assert recorder.names == []


def test_an_error_of_a_step_is_not_hidden_as_a_failed_check(recorder, make_action) -> None:
    """Only a failed expectation is recorded; a step that breaks is a different kind of news."""

    def explode(text: str) -> str:
        raise RuntimeError("boom")

    profile = Profile("generic", "broken", description="Broken", steps=make_action(explode, name="Explode"))
    with pytest.raises(RuntimeError, match="boom"):
        assert_profile_steps(recorder, profile, {".py": [("a", "a")]})


def test_the_intro_is_the_start_of_every_name(recorder, make_profile) -> None:
    assert_profile_steps(
        recorder,
        make_profile(),
        {".py": [("a", "A")], ".xyz": [("b", "b")]},
        unchanged_suffixes=(),
        cover_all_suffixes=True,
        intro="[x] ",
    )
    assert recorder.names and all(name.startswith("[x] test_") for name in recorder.names)


@pytest.mark.parametrize("not_a_profile", ["python/clean", None, 42])
def test_something_that_is_not_a_profile_is_refused_at_once(recorder, not_a_profile) -> None:
    with pytest.raises(AssertionError, match="expects a Profile instance"):
        assert_profile_steps(recorder, not_a_profile, {".py": [("a", "A")]})
    assert recorder.names == []
