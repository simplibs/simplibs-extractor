from simplibs.extractor.definitions import Profile
from simplibs.extractor.registry import list_systems, register_profile
from simplibs.extractor.registry._helpers import PROFILE_REGISTRY


def test_lists_the_built_in_system() -> None:
    assert "generic" in list_systems()


def test_every_system_once_sorted() -> None:
    PROFILE_REGISTRY.clear()
    for system, name in [("web", "a"), ("python", "a"), ("python", "b"), ("generic", "all")]:
        register_profile(Profile(system, name))
    assert list_systems() == ["generic", "python", "web"]


def test_empty_registry_has_no_systems() -> None:
    PROFILE_REGISTRY.clear()
    assert list_systems() == []


def test_returns_a_new_list_every_time() -> None:
    systems = list_systems()
    systems.append("invented")
    assert "invented" not in list_systems()
