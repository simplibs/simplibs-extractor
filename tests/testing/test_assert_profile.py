import pytest
from simplibs.extractor.testing import assert_profile

COMPLETE = dict(
    expected_key="python/clean",
    expected_output_name="python_clean.md",
    expected_format="markdown",
    expected_description="Python without tests",
    included=("pkg/a.py",),
    excluded=("tests/test_a.py", "readme.md"),
    step_cases={".py": [("ab", "AB")], ".xyz": [(" a ", "a")]},
    unchanged_suffixes=(),
    cover_all_suffixes=True,
)


def test_a_correct_profile_passes_every_blade(recorder, make_profile) -> None:
    assert_profile(recorder, make_profile(), **COMPLETE)
    assert recorder.failed == {}
    assert len(recorder.passed) == 5 + 3 + 2 + 1


def test_works_with_the_real_subtests_fixture(subtests, make_profile) -> None:
    assert_profile(subtests, make_profile(), **COMPLETE)


def test_the_key_of_the_profile_groups_every_name(recorder, make_profile) -> None:
    assert_profile(recorder, make_profile(), **COMPLETE)
    assert all(name.startswith("[python/clean] test_") for name in recorder.names)


def test_the_three_blades_each_leave_their_trace(recorder, make_profile) -> None:
    assert_profile(recorder, make_profile(), **COMPLETE)
    names = recorder.names
    assert "[python/clean] test_key" in names
    assert "[python/clean] test_selected_#index_0_pkg/a.py" in names
    assert "[python/clean] test_steps_.py_#index_0" in names
    assert "[python/clean] test_every_suffix_has_a_case" in names


def test_a_given_intro_replaces_the_key_as_the_prefix(recorder, make_profile) -> None:
    assert_profile(recorder, make_profile(), **COMPLETE, intro="mine")
    assert recorder.names and all(name.startswith("mine test_") for name in recorder.names)


def test_without_data_only_the_identity_is_checked(recorder, make_profile) -> None:
    assert_profile(recorder, make_profile(), expected_key="python/clean")
    assert recorder.passed == [
        "[python/clean] test_key",
        "[python/clean] test_description_is_one_line",
    ]


def test_the_selection_runs_when_only_excluded_paths_are_given(recorder, make_profile) -> None:
    assert_profile(recorder, make_profile(), expected_key="python/clean", excluded=("readme.md",))
    assert "[python/clean] test_left_out_#index_0_readme.md" in recorder.passed
    assert not any("test_steps_" in name or "test_no_step_" in name for name in recorder.names)


def test_the_selection_runs_when_only_included_paths_are_given(recorder, make_profile) -> None:
    assert_profile(recorder, make_profile(), expected_key="python/clean", included=("a.py",))
    assert "[python/clean] test_selected_#index_0_a.py" in recorder.passed


def test_the_steps_run_when_only_unchanged_suffixes_are_given(recorder, make_action, make_profile) -> None:
    profile = make_profile(steps={".py": make_action(str.upper, name="Upper")})
    assert_profile(recorder, profile, expected_key="python/clean", unchanged_suffixes=(".md",))
    assert "[python/clean] test_no_step_#index_0_.md" in recorder.passed
    assert not any("test_selected_" in name or "test_left_out_" in name for name in recorder.names)


def test_the_steps_run_when_only_the_coverage_is_asked(recorder, make_profile) -> None:
    assert_profile(recorder, make_profile(), expected_key="python/clean", cover_all_suffixes=True)
    assert list(recorder.failed) == ["[python/clean] test_every_suffix_has_a_case"]


def test_a_failure_in_each_blade_is_reported_and_the_rest_goes_on(recorder, make_profile) -> None:
    assert_profile(
        recorder,
        make_profile(),
        expected_key="python/other",
        included=("a.py", "readme.md"),
        excluded=("tests/a.py",),
        step_cases={".py": [("ab", "ab")]},
    )
    assert set(recorder.failed) == {
        "[python/clean] test_key",
        "[python/clean] test_selected_#index_1_readme.md",
        "[python/clean] test_steps_.py_#index_0",
    }
    assert "[python/clean] test_selected_#index_0_a.py" in recorder.passed
    assert "[python/clean] test_left_out_#index_0_tests/a.py" in recorder.passed


def test_the_values_reach_the_blades(recorder, make_profile) -> None:
    """Each pinned value is compared: a wrong one fails in its own subtest."""
    assert_profile(
        recorder,
        make_profile(),
        expected_key="python/clean",
        expected_output_name="x.md",
        expected_format="plain",
        expected_description="Other",
    )
    assert set(recorder.failed) == {
        "[python/clean] test_output_name",
        "[python/clean] test_format",
        "[python/clean] test_description_expected_text",
    }


def test_a_path_in_both_lists_is_refused_before_any_check_of_the_selection(recorder, make_profile) -> None:
    with pytest.raises(AssertionError, match="both included and excluded"):
        assert_profile(recorder, make_profile(), expected_key="python/clean", included=("a.py",), excluded=("a.py",))


def test_a_suffix_that_is_no_suffix_is_refused(recorder, make_profile) -> None:
    with pytest.raises(AssertionError, match="file suffixes"):
        assert_profile(recorder, make_profile(), expected_key="python/clean", step_cases={"py": [("a", "A")]})


@pytest.mark.parametrize("not_a_profile", ["python/clean", None, 42, object])
def test_something_that_is_not_a_profile_is_refused_at_once(recorder, not_a_profile) -> None:
    with pytest.raises(AssertionError, match="expects a Profile instance"):
        assert_profile(recorder, not_a_profile, expected_key="python/clean")
    assert recorder.names == []


def test_the_profile_is_accepted_whatever_its_steps_look_like(recorder, make_profile) -> None:
    """None, one action and a mapping are the three shapes of `StepsSpec`."""
    for steps in (None, {}, {"*": make_profile().steps["*"]}):
        assert_profile(recorder, make_profile(steps=steps), expected_key="python/clean", unchanged_suffixes=())
    assert recorder.failed == {}


def test_assert_profile_is_the_public_name_of_the_testing_package() -> None:
    import simplibs.extractor.testing as testing

    assert testing.__all__ == ["assert_profile"]
    assert testing.assert_profile is assert_profile
