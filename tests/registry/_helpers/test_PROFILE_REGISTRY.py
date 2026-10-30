from simplibs.extractor.constants import DEFAULT_PROFILE_KEY
from simplibs.extractor.registry._helpers import GENERIC_ALL, PROFILE_REGISTRY


def test_is_a_dict_keyed_by_profile_key() -> None:
    assert isinstance(PROFILE_REGISTRY, dict)
    for key, profile in PROFILE_REGISTRY.items():
        assert key == profile.key


def test_built_in_profile_is_registered_at_import() -> None:
    """`generic/all` exists as soon as the registry is imported."""
    assert PROFILE_REGISTRY[DEFAULT_PROFILE_KEY] is GENERIC_ALL
