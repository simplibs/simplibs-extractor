import pytest
from simplibs.exception import ValidationError
from simplibs.extractor.constants import DEFAULT_PROFILE_KEY
from simplibs.extractor.definitions import Profile
from simplibs.extractor.registry import list_profiles, register_profile
from simplibs.extractor.registry._helpers import GENERIC_ALL, PROFILE_REGISTRY


def _fill() -> None:
    PROFILE_REGISTRY.clear()
    for system, name in [("python", "b"), ("web", "a"), ("python", "a"), ("generic", "all")]:
        register_profile(Profile(system, name))


def test_lists_every_profile_sorted_by_key() -> None:
    _fill()
    assert [profile.key for profile in list_profiles()] == ["generic/all", "python/a", "python/b", "web/a"]


def test_built_in_profile_is_in_the_listing() -> None:
    assert GENERIC_ALL in list_profiles()
    assert DEFAULT_PROFILE_KEY in [profile.key for profile in list_profiles()]


def test_narrows_to_one_system() -> None:
    _fill()
    assert [profile.key for profile in list_profiles("python")] == ["python/a", "python/b"]
    assert [profile.key for profile in list_profiles(system="web")] == ["web/a"]


def test_unknown_system_gives_an_empty_list() -> None:
    _fill()
    assert list_profiles("nothing") == []


def test_none_means_all() -> None:
    _fill()
    assert list_profiles(None) == list_profiles()


def test_system_match_is_exact() -> None:
    _fill()
    assert list_profiles("Python") == []
    assert list_profiles("pyth") == []


def test_returns_a_new_list_every_time() -> None:
    """Changing the result does not touch the registry."""
    first = list_profiles()
    first.clear()
    assert list_profiles() != []
    assert list_profiles() is not list_profiles()


def test_a_newly_registered_profile_appears() -> None:
    register_profile(Profile("python", "code"))
    assert "python/code" in [profile.key for profile in list_profiles()]


@pytest.mark.parametrize("system", [5, b"python", ["python"]])
def test_system_must_be_text_or_none(system) -> None:
    with pytest.raises(ValidationError):
        list_profiles(system)
