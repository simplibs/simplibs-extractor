import argparse
import pytest
from simplibs.exception import ParamError
from simplibs.exception.testing import assert_exception_function
from simplibs.extractor.cli import handle_list_options
from simplibs.extractor.definitions import Profile
from simplibs.extractor.registry import register_profile
from simplibs.extractor.registry._helpers import PROFILE_REGISTRY


@pytest.fixture(autouse=True)
def some_profiles():
    register_profile(Profile("python", "a", description="Alpha"))
    register_profile(Profile("python", "b", description="Beta"))


def _args(list_systems: bool = False, list_profiles: str | None = None) -> argparse.Namespace:
    return argparse.Namespace(list_systems=list_systems, list_profiles=list_profiles)


# ---------------------------------------------------------------- no question

def test_no_list_asked_means_false_and_silence(capsys) -> None:
    assert handle_list_options(_args()) is False
    assert capsys.readouterr().out == ""


def test_an_empty_system_name_is_no_question(capsys) -> None:
    assert handle_list_options(_args(list_profiles="")) is False
    assert capsys.readouterr().out == ""


# ---------------------------------------------------------------- systems

def test_the_systems_are_listed_with_their_profile_counts(capsys) -> None:
    assert handle_list_options(_args(list_systems=True)) is True
    assert capsys.readouterr().out == "Systems:\n  generic - 1 profile(s)\n  python  - 2 profile(s)\n\n"


def test_an_empty_registry_lists_no_systems(capsys) -> None:
    PROFILE_REGISTRY.clear()
    assert handle_list_options(_args(list_systems=True)) is True
    assert capsys.readouterr().out == "Systems:\n\n"


def test_the_systems_list_goes_to_standard_output_only(capsys) -> None:
    handle_list_options(_args(list_systems=True))
    assert capsys.readouterr().err == ""


# ---------------------------------------------------------------- profiles of a system

def test_the_profiles_of_a_system_are_listed_with_their_descriptions(capsys) -> None:
    assert handle_list_options(_args(list_profiles="python")) is True
    assert capsys.readouterr().out == "Profiles of python:\n  a - Alpha\n  b - Beta\n\n"


def test_the_profiles_are_listed_by_name_not_by_full_key(capsys) -> None:
    handle_list_options(_args(list_profiles="generic"))
    printed = capsys.readouterr().out
    assert "  all - " in printed
    assert "generic/all" not in printed


def test_an_unknown_system_gives_a_config_card_that_names_the_known_ones(subtests, capsys) -> None:
    assert_exception_function(
        subtests,
        lambda system: handle_list_options(_args(list_profiles=system)),
        invalid_params=("nothing",),
        valid_params=("python",),
        exception_type=ParamError,
        error_name="EXTRACTOR_CONFIG_INVALID",
        label="option '--list-profiles'",
        value="nothing",
        problem="No profile is registered for the system 'nothing'.",
        expected="One of the registered systems: generic, python.",
        verbose=False,
    )


def test_an_unknown_system_prints_no_list(capsys) -> None:
    with pytest.raises(ParamError):
        handle_list_options(_args(list_profiles="nothing"))
    assert capsys.readouterr().out == ""


# ---------------------------------------------------------------- both asked

def test_when_both_are_asked_the_systems_come_first_and_alone(capsys) -> None:
    assert handle_list_options(_args(list_systems=True, list_profiles="python")) is True
    printed = capsys.readouterr().out
    assert printed.startswith("Systems:")
    assert "Profiles of" not in printed
