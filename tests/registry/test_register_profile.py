import pytest
from simplibs.exception import AlreadyExistsError, ValidationError
from simplibs.exception.testing import assert_exception_function
from simplibs.extractor.constants import DEFAULT_PROFILE_KEY
from simplibs.extractor.definitions import Profile
from simplibs.extractor.registry import get_profile, register_profile
from simplibs.extractor.registry._helpers import GENERIC_ALL, PROFILE_REGISTRY


def test_registers_a_profile_under_its_key() -> None:
    profile = Profile("python", "code")
    register_profile(profile)
    assert PROFILE_REGISTRY["python/code"] is profile
    assert get_profile("python/code") is profile


def test_returns_the_registered_profile() -> None:
    """So the call can be used as an expression."""
    profile = Profile("python", "code")
    assert register_profile(profile) is profile


def test_two_profiles_of_one_system_live_side_by_side() -> None:
    first, second = Profile("python", "a"), Profile("python", "b")
    register_profile(first)
    register_profile(second)
    assert get_profile("python/a") is first
    assert get_profile("python/b") is second


def test_taken_key_gives_an_already_exists_card(subtests) -> None:
    """A second profile under a taken key is refused (the built-in key is taken from the start)."""
    assert_exception_function(
        subtests,
        lambda profile: register_profile(profile),
        invalid_params=(GENERIC_ALL,),
        valid_params=(Profile("python", "new"),),
        exception_type=AlreadyExistsError,
        error_name="EXTRACTOR_PROFILE_EXISTS",
        label=f"profile '{DEFAULT_PROFILE_KEY}'",
        value=DEFAULT_PROFILE_KEY,
        verbose=False,
    )


def test_refused_registration_keeps_the_original() -> None:
    original = Profile("python", "code", description="original")
    register_profile(original)
    with pytest.raises(AlreadyExistsError):
        register_profile(Profile("python", "code", description="newcomer"))
    assert get_profile("python/code") is original


def test_replace_existing_replaces() -> None:
    original = Profile("python", "code", description="original")
    newcomer = Profile("python", "code", description="newcomer")
    register_profile(original)
    assert register_profile(newcomer, replace_existing=True) is newcomer
    assert get_profile("python/code") is newcomer


def test_replace_existing_on_a_free_key_just_registers() -> None:
    profile = Profile("python", "fresh")
    register_profile(profile, replace_existing=True)
    assert get_profile("python/fresh") is profile


@pytest.mark.parametrize("value", ["python/code", None, 5, {"system": "python"}])
def test_only_a_profile_is_accepted(value) -> None:
    with pytest.raises(ValidationError):
        register_profile(value)


def test_replace_existing_must_be_a_bool() -> None:
    with pytest.raises(ValidationError):
        register_profile(Profile("python", "x"), replace_existing="yes")


def test_replace_existing_is_keyword_only() -> None:
    with pytest.raises(TypeError):
        register_profile(Profile("python", "x"), True)  # type: ignore[misc]
