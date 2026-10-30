import pytest
from simplibs.extractor.cli._helpers import is_profile_reference
from simplibs.extractor.definitions import Profile
from simplibs.extractor.registry import register_profile


@pytest.fixture(autouse=True)
def some_profiles():
    register_profile(Profile("python", "a"))
    register_profile(Profile("web", "b"))


@pytest.mark.parametrize("value", ["generic", "python", "web"])
def test_a_registered_system_is_a_reference(value) -> None:
    assert is_profile_reference(value) is True


@pytest.mark.parametrize("value", ["generic/all", "python/a", "web/b"])
def test_a_registered_full_key_is_a_reference(value) -> None:
    assert is_profile_reference(value) is True


@pytest.mark.parametrize("value", ["python/a,web/b", "python/a, web/b", " python/a ,web/b ", "generic/all,python/a,web/b"])
def test_a_comma_list_of_registered_keys_is_a_reference(value) -> None:
    assert is_profile_reference(value) is True


@pytest.mark.parametrize(
    "value",
    [
        "./src",
        "src",
        "nothing",
        "",
        "python/nothing",          # a full key that is not registered
        "python/a,python/nothing",  # one bad part spoils the list
        "python/a,",                # an empty part
        ",",
        "Python",                   # case matters
        "python/A",
        "C:\\Users\\me\\project",
    ],
)
def test_anything_else_is_not_a_reference(value) -> None:
    assert is_profile_reference(value) is False


def test_the_answer_follows_the_registry() -> None:
    assert is_profile_reference("late/arrival") is False
    register_profile(Profile("late", "arrival"))
    assert is_profile_reference("late/arrival") is True
    assert is_profile_reference("late") is True
