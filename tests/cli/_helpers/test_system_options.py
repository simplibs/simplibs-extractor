from simplibs.extractor.cli._helpers import system_options
from simplibs.extractor.definitions import Profile
from simplibs.extractor.registry import register_profile
from simplibs.extractor.registry._helpers import PROFILE_REGISTRY


def test_the_built_in_system_is_there() -> None:
    assert system_options()["generic"] == "1 profile(s)"


def test_every_system_with_the_number_of_its_profiles() -> None:
    register_profile(Profile("python", "a"))
    register_profile(Profile("python", "b"))
    register_profile(Profile("web", "c"))
    assert system_options() == {"generic": "1 profile(s)", "python": "2 profile(s)", "web": "1 profile(s)"}


def test_the_order_is_by_system() -> None:
    register_profile(Profile("zeta", "a"))
    register_profile(Profile("alpha", "a"))
    assert list(system_options()) == ["alpha", "generic", "zeta"]


def test_the_count_follows_the_registry() -> None:
    register_profile(Profile("python", "a"))
    assert system_options()["python"] == "1 profile(s)"
    register_profile(Profile("python", "b"))
    assert system_options()["python"] == "2 profile(s)"


def test_an_empty_registry_gives_an_empty_dictionary() -> None:
    PROFILE_REGISTRY.clear()
    assert system_options() == {}
