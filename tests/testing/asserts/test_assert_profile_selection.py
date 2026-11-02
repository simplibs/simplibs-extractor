import pytest
from simplibs.extractor.definitions import Profile
from simplibs.extractor.testing.asserts import assert_profile_selection


def test_a_correct_profile_passes_every_path(recorder, make_profile) -> None:
    assert_profile_selection(
        recorder,
        make_profile(),
        included=("pkg/a.py", "a.py"),
        excluded=("tests/test_a.py", "readme.md"),
    )
    assert recorder.failed == {}
    assert recorder.passed == [
        "test_selected_#index_0_pkg/a.py",
        "test_selected_#index_1_a.py",
        "test_left_out_#index_0_tests/test_a.py",
        "test_left_out_#index_1_readme.md",
    ]


def test_works_with_the_real_subtests_fixture(subtests, make_profile) -> None:
    assert_profile_selection(subtests, make_profile(), included=("pkg/a.py",), excluded=("tests/test_a.py",))


def test_no_paths_open_no_subtests(recorder, make_profile) -> None:
    assert_profile_selection(recorder, make_profile(), included=(), excluded=())
    assert recorder.names == []


def test_a_path_the_include_rule_does_not_accept_fails_as_included(recorder, make_profile) -> None:
    assert_profile_selection(recorder, make_profile(), included=("readme.md",), excluded=())
    assert list(recorder.failed) == ["test_selected_#index_0_readme.md"]
    message = recorder.failed["test_selected_#index_0_readme.md"]
    assert "'readme.md'" in message
    assert "include rule does not accept it" in message


def test_a_path_the_exclude_rule_matches_fails_as_included(recorder, make_profile) -> None:
    """The `include` rule accepts it, the `exclude` rule takes it away: `exclude` wins."""
    assert_profile_selection(recorder, make_profile(), included=("tests/test_a.py",), excluded=())
    message = recorder.failed["test_selected_#index_0_tests/test_a.py"]
    assert "exclude rule matches it" in message


def test_a_path_the_profile_takes_fails_as_excluded(recorder, make_profile) -> None:
    assert_profile_selection(recorder, make_profile(), included=(), excluded=("pkg/a.py",))
    assert list(recorder.failed) == ["test_left_out_#index_0_pkg/a.py"]
    assert "the profile takes it" in recorder.failed["test_left_out_#index_0_pkg/a.py"]


@pytest.mark.parametrize("path", ["readme.md", "tests/test_a.py", "pkg/tests/deep/test_a.py"], ids=["by-include", "by-exclude", "by-any-parent"])
def test_a_path_is_left_out_by_either_rule(recorder, make_profile, path) -> None:
    assert_profile_selection(recorder, make_profile(), included=(), excluded=(path,))
    assert recorder.failed == {}


def test_a_folder_name_is_compared_as_a_whole(recorder, make_profile) -> None:
    """`testsuite` and `latest` are not `tests`: the exclude rule judges whole folder names of the relative path."""
    assert_profile_selection(recorder, make_profile(), included=("testsuite/a.py", "latest/a.py"), excluded=())
    assert recorder.failed == {}


def test_a_profile_without_rules_takes_every_path(recorder) -> None:
    profile = Profile("generic", "everything", description="Everything")
    assert_profile_selection(recorder, profile, included=("a.py", "x/y/z.bin", "readme"), excluded=())
    assert recorder.failed == {}


def test_a_profile_without_rules_leaves_nothing_out(recorder) -> None:
    profile = Profile("generic", "everything", description="Everything")
    assert_profile_selection(recorder, profile, included=(), excluded=("a.py",))
    assert list(recorder.failed) == ["test_left_out_#index_0_a.py"]


def test_a_profile_with_only_an_exclude_rule(recorder, make_profile) -> None:
    profile = make_profile(include=None)
    assert_profile_selection(recorder, profile, included=("readme.md", "a.py"), excluded=("tests/a.py",))
    assert recorder.failed == {}


def test_every_path_is_reported_on_its_own(recorder, make_profile) -> None:
    assert_profile_selection(
        recorder,
        make_profile(),
        included=("a.py", "readme.md"),
        excluded=("tests/a.py", "b.py"),
    )
    assert set(recorder.failed) == {"test_selected_#index_1_readme.md", "test_left_out_#index_1_b.py"}
    assert len(recorder.passed) == 2


def test_the_intro_is_the_start_of_every_name(recorder, make_profile) -> None:
    assert_profile_selection(recorder, make_profile(), included=("a.py",), excluded=("b.md",), intro="[x] ")
    assert recorder.names and all(name.startswith("[x] test_") for name in recorder.names)


def test_a_path_in_both_lists_is_refused_at_once(recorder, make_profile) -> None:
    with pytest.raises(AssertionError, match="both included and excluded"):
        assert_profile_selection(recorder, make_profile(), included=("a.py", "b.py"), excluded=("b.py",))
    assert recorder.names == []


@pytest.mark.parametrize("not_a_profile", ["python/clean", None, 42])
def test_something_that_is_not_a_profile_is_refused_at_once(recorder, not_a_profile) -> None:
    with pytest.raises(AssertionError, match="expects a Profile instance"):
        assert_profile_selection(recorder, not_a_profile, included=("a.py",), excluded=())
    assert recorder.names == []
