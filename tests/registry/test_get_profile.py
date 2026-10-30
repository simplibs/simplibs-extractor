import pytest
from simplibs.exception import NotFoundError, ValidationError
from simplibs.exception.testing import assert_exception_function
from simplibs.extractor.constants import DEFAULT_PROFILE_KEY
from simplibs.extractor.definitions import Profile
from simplibs.extractor.registry import get_profile, register_profile
from simplibs.extractor.registry._helpers import GENERIC_ALL, PROFILE_REGISTRY


def test_built_in_profile_is_always_there() -> None:
    assert get_profile(DEFAULT_PROFILE_KEY) is GENERIC_ALL


def test_returns_a_registered_profile() -> None:
    profile = register_profile(Profile("python", "code"))
    assert get_profile("python/code") is profile


def test_unknown_key_gives_a_not_found_card_listing_the_registered_keys(subtests) -> None:
    """The card names what exists, sorted, so a typo can be spotted at once."""
    PROFILE_REGISTRY.clear()
    register_profile(Profile("b", "x"))
    register_profile(Profile("a", "y"))
    register_profile(GENERIC_ALL)
    assert_exception_function(
        subtests,
        get_profile,
        invalid_params=("python/missing",),
        valid_params=("a/y",),
        exception_type=NotFoundError,
        error_name="EXTRACTOR_PROFILE_NOT_FOUND",
        label="profile 'python/missing'",
        value="python/missing",
        problem="No profile is registered under 'python/missing'.",
        expected="One of the registered profiles: a/y, b/x, generic/all.",
        exception=LookupError,
        verbose=False,
    )


def test_empty_registry_says_so(subtests) -> None:
    PROFILE_REGISTRY.clear()
    assert_exception_function(
        subtests,
        get_profile,
        invalid_params=("python/code",),
        exception_type=NotFoundError,
        error_name="EXTRACTOR_PROFILE_NOT_FOUND",
        expected="One of the registered profiles: (none registered).",
        verbose=False,
    )


@pytest.mark.parametrize("key", ["Generic/All", "generic/ALL", " generic/all", "generic/all ", "generic", ""])
def test_the_key_must_match_exactly(key) -> None:
    """No case folding, no trimming, no partial keys."""
    with pytest.raises(NotFoundError):
        get_profile(key)


@pytest.mark.parametrize("key", [None, 5, b"generic/all", ["generic/all"]])
def test_the_key_must_be_text(key) -> None:
    with pytest.raises(ValidationError):
        get_profile(key)
