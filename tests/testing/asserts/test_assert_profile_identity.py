import pytest
from simplibs.extractor.testing.asserts import assert_profile_identity


def test_a_correct_profile_passes_every_check(recorder, make_profile) -> None:
    assert_profile_identity(
        recorder,
        make_profile(),
        expected_key="python/clean",
        expected_output_name="python_clean.md",
        expected_format="markdown",
        expected_description="Python without tests",
    )
    assert recorder.failed == {}
    assert recorder.passed == [
        "test_key",
        "test_description_is_one_line",
        "test_description_expected_text",
        "test_output_name",
        "test_format",
    ]


def test_works_with_the_real_subtests_fixture(subtests, make_profile) -> None:
    assert_profile_identity(subtests, make_profile(), expected_key="python/clean", expected_output_name="python_clean.md")


def test_only_the_key_and_the_description_are_checked_without_the_optional_values(recorder, make_profile) -> None:
    """The output name, the format and the exact description are pinned only when given."""
    assert_profile_identity(recorder, make_profile(output_name="other.md", format="plain"), expected_key="python/clean")
    assert recorder.failed == {}
    assert recorder.passed == ["test_key", "test_description_is_one_line"]


def test_a_wrong_key_fails_only_the_key_check(recorder, make_profile) -> None:
    assert_profile_identity(recorder, make_profile(), expected_key="python/other")
    assert list(recorder.failed) == ["test_key"]
    assert "'python/other'" in recorder.failed["test_key"]
    assert "'python/clean'" in recorder.failed["test_key"]


@pytest.mark.parametrize("description", ["", "   "], ids=["empty", "blank"])
def test_a_blank_description_fails(recorder, make_profile, description) -> None:
    """`Profile` allows it; a profile that the listing shows with an empty line is not acceptable."""
    assert_profile_identity(recorder, make_profile(description=description), expected_key="python/clean")
    assert list(recorder.failed) == ["test_description_is_one_line"]
    assert "non-blank" in recorder.failed["test_description_is_one_line"]


def test_a_description_of_several_lines_fails(recorder, make_profile) -> None:
    assert_profile_identity(recorder, make_profile(description="First\nSecond"), expected_key="python/clean")
    assert list(recorder.failed) == ["test_description_is_one_line"]
    assert "one-line" in recorder.failed["test_description_is_one_line"]


def test_a_line_break_around_the_text_is_not_several_lines(recorder, make_profile) -> None:
    assert_profile_identity(recorder, make_profile(description="One line\n"), expected_key="python/clean")
    assert recorder.failed == {}


def test_a_wrong_description_fails_only_the_exact_text_check(recorder, make_profile) -> None:
    assert_profile_identity(recorder, make_profile(), expected_key="python/clean", expected_description="Something else")
    assert list(recorder.failed) == ["test_description_expected_text"]
    assert "'Something else'" in recorder.failed["test_description_expected_text"]


def test_a_wrong_output_name_fails_only_the_output_name_check(recorder, make_profile) -> None:
    assert_profile_identity(recorder, make_profile(), expected_key="python/clean", expected_output_name="other.md")
    assert list(recorder.failed) == ["test_output_name"]
    assert "'other.md'" in recorder.failed["test_output_name"]
    assert "'python_clean.md'" in recorder.failed["test_output_name"]


def test_a_wrong_format_fails_only_the_format_check(recorder, make_profile) -> None:
    assert_profile_identity(recorder, make_profile(), expected_key="python/clean", expected_format="plain")
    assert list(recorder.failed) == ["test_format"]
    assert "'plain'" in recorder.failed["test_format"]


def test_every_check_is_reported_on_its_own(recorder, make_profile) -> None:
    """One wrong value does not hide the others."""
    assert_profile_identity(
        recorder,
        make_profile(description=""),
        expected_key="python/other",
        expected_output_name="other.md",
        expected_format="plain",
    )
    assert set(recorder.failed) == {"test_key", "test_description_is_one_line", "test_output_name", "test_format"}


def test_the_intro_is_the_start_of_every_name(recorder, make_profile) -> None:
    assert_profile_identity(
        recorder,
        make_profile(),
        expected_key="python/clean",
        expected_output_name="python_clean.md",
        expected_format="markdown",
        expected_description="Python without tests",
        intro="[x] ",
    )
    assert recorder.names and all(name.startswith("[x] test_") for name in recorder.names)


@pytest.mark.parametrize("not_a_profile", ["python/clean", None, 42, object])
def test_something_that_is_not_a_profile_is_refused_at_once(recorder, not_a_profile) -> None:
    with pytest.raises(AssertionError, match="expects a Profile instance"):
        assert_profile_identity(recorder, not_a_profile, expected_key="python/clean")
    assert recorder.names == []
