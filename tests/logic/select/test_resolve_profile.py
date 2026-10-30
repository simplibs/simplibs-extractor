import pytest
from simplibs.exception import NotFoundError
from simplibs.exception.testing import assert_exception_function
from simplibs.extractor.definitions import Profile
from simplibs.extractor.logic.select import resolve_profile
from simplibs.extractor.registry import register_profile
from simplibs.extractor.registry._helpers import GENERIC_ALL


def test_none_gives_the_built_in_profile() -> None:
    assert resolve_profile(None) is GENERIC_ALL


def test_a_profile_is_returned_as_it_is() -> None:
    """Even a profile that was never registered is used directly."""
    profile = Profile("python", "unregistered")
    assert resolve_profile(profile) is profile


def test_a_profile_wins_over_a_registered_one_with_the_same_key() -> None:
    registered = register_profile(Profile("python", "code", description="registered"))
    given = Profile("python", "code", description="given")
    assert resolve_profile(given) is given
    assert resolve_profile(given) is not registered


def test_a_key_gives_the_registered_profile() -> None:
    registered = register_profile(Profile("python", "code"))
    assert resolve_profile("python/code") is registered


def test_the_default_key_gives_the_built_in_profile() -> None:
    assert resolve_profile("generic/all") is GENERIC_ALL


def test_an_unknown_key_gives_a_not_found_card(subtests) -> None:
    assert_exception_function(
        subtests,
        resolve_profile,
        invalid_params=("python/missing",),
        valid_params=("generic/all",),
        exception_type=NotFoundError,
        error_name="EXTRACTOR_PROFILE_NOT_FOUND",
        label="profile 'python/missing'",
        value="python/missing",
        verbose=False,
    )
