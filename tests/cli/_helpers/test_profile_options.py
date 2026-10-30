from simplibs.extractor.cli._helpers import profile_options
from simplibs.extractor.definitions import Profile
from simplibs.extractor.registry import register_profile
from simplibs.extractor.registry._helpers import PROFILE_REGISTRY


def test_the_profiles_of_a_system_by_their_own_names() -> None:
    register_profile(Profile("python", "b", description="Beta"))
    register_profile(Profile("python", "a", description="Alpha"))
    assert profile_options("python") == {"a": "Alpha", "b": "Beta"}


def test_the_order_is_by_name() -> None:
    register_profile(Profile("python", "zeta"))
    register_profile(Profile("python", "alpha"))
    register_profile(Profile("python", "mid"))
    assert list(profile_options("python")) == ["alpha", "mid", "zeta"]


def test_other_systems_are_left_out() -> None:
    register_profile(Profile("python", "a"))
    register_profile(Profile("web", "b"))
    assert list(profile_options("python")) == ["a"]


def test_an_empty_description_stays_empty() -> None:
    register_profile(Profile("python", "a"))
    assert profile_options("python") == {"a": ""}


def test_the_built_in_system() -> None:
    options = profile_options("generic")
    assert list(options) == ["all"]
    assert options["all"].strip()


def test_an_unknown_system_gives_an_empty_dictionary() -> None:
    assert profile_options("nothing") == {}


def test_the_name_of_a_system_must_match_exactly() -> None:
    register_profile(Profile("python", "a"))
    assert profile_options("Python") == {}


def test_an_empty_registry_gives_an_empty_dictionary() -> None:
    PROFILE_REGISTRY.clear()
    assert profile_options("generic") == {}
