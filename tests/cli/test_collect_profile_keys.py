import argparse
import sys
import pytest
from simplibs.exception import ParamError, StateError
from simplibs.exception.testing import assert_exception_function
from simplibs.extractor.cli import collect_profile_keys
from simplibs.extractor.definitions import Profile
from simplibs.extractor.registry import register_profile

# `simplibs.extractor.cli.collect_profile_keys` is also the name of the function, so the MODULE is taken from `sys.modules`.
MODULE = sys.modules["simplibs.extractor.cli.collect_profile_keys"]


class Prompts:
    """Replacements for the two questions of the wizard; they record what they were asked."""

    def __init__(self) -> None:
        self.system_answer = "python"
        self.profile_answer: list[str] = ["a"]
        self.system_questions: list[tuple[str, dict]] = []
        self.profile_questions: list[tuple[str, dict]] = []

    def choice(self, label, options, *args, **kwargs):
        self.system_questions.append((label, dict(options)))
        return self.system_answer

    def multi(self, label, options, *args, **kwargs):
        self.profile_questions.append((label, dict(options)))
        return self.profile_answer


@pytest.fixture
def prompts(monkeypatch) -> Prompts:
    fake = Prompts()
    monkeypatch.setattr(MODULE, "prompt_choice", fake.choice)
    monkeypatch.setattr(MODULE, "prompt_multi_choice", fake.multi)
    return fake


@pytest.fixture(autouse=True)
def some_profiles():
    register_profile(Profile("python", "a", description="Alpha"))
    register_profile(Profile("python", "b", description="Beta"))


def _args(system=None, profiles=None) -> argparse.Namespace:
    return argparse.Namespace(system=system, profiles=profiles)


# ---------------------------------------------------------------- given on the command line

def test_system_and_names_are_expanded() -> None:
    assert collect_profile_keys(_args("python", "a,b")) == ["python/a", "python/b"]


def test_full_keys_are_kept() -> None:
    assert collect_profile_keys(_args(None, "generic/all,python/a")) == ["generic/all", "python/a"]


def test_the_order_given_is_kept() -> None:
    assert collect_profile_keys(_args("python", "b,a")) == ["python/b", "python/a"]


def test_nobody_is_asked_when_the_profiles_are_given(prompts, terminals) -> None:
    terminals(stdin=True, stdout=True)
    collect_profile_keys(_args("python", "a"))
    assert prompts.system_questions == [] and prompts.profile_questions == []


def test_given_profiles_need_no_terminal(prompts) -> None:
    """A script or a CI job with all the words typed never meets a question."""
    assert collect_profile_keys(_args("python", "a")) == ["python/a"]


# ---------------------------------------------------------------- missing, and nobody to ask

@pytest.mark.parametrize("args", [_args(), _args("python"), _args(None, "")])
def test_missing_profiles_without_a_terminal_give_a_state_card(args, prompts) -> None:
    with pytest.raises(StateError) as caught:
        collect_profile_keys(args)
    assert caught.value.error_name == "CLI_NOT_INTERACTIVE"
    assert "no profile was given" in str(caught.value)
    assert prompts.system_questions == [] and prompts.profile_questions == []


def test_a_terminal_for_input_only_is_not_enough(prompts, terminals) -> None:
    terminals(stdin=True, stdout=False)
    with pytest.raises(StateError):
        collect_profile_keys(_args())


# ---------------------------------------------------------------- the wizard

def test_a_given_system_is_not_asked_again_but_the_profiles_are(prompts, terminals) -> None:
    terminals(stdin=True, stdout=True)
    prompts.profile_answer = ["a", "b"]

    keys = collect_profile_keys(_args("python"))

    assert keys == ["python/a", "python/b"]
    assert prompts.system_questions == []
    assert prompts.profile_questions == [("Profiles", {"a": "Alpha", "b": "Beta"})]


def test_a_missing_system_is_asked_first(prompts, terminals) -> None:
    terminals(stdin=True, stdout=True)
    prompts.system_answer = "python"
    prompts.profile_answer = ["b"]

    keys = collect_profile_keys(_args())

    assert keys == ["python/b"]
    assert prompts.system_questions == [("System", {"generic": "1 profile(s)", "python": "2 profile(s)"})]
    assert prompts.profile_questions == [("Profiles", {"a": "Alpha", "b": "Beta"})]


def test_the_answers_may_be_any_sequence(prompts, terminals) -> None:
    terminals(stdin=True, stdout=True)
    prompts.profile_answer = ("b", "a")
    assert collect_profile_keys(_args("python")) == ["python/b", "python/a"]


def test_the_choice_of_the_default_system(prompts, terminals) -> None:
    terminals(stdin=True, stdout=True)
    prompts.system_answer = "generic"
    prompts.profile_answer = ["all"]
    assert collect_profile_keys(_args()) == ["generic/all"]


def test_a_system_without_profiles_gives_a_config_card_that_names_the_known_systems(subtests, prompts, terminals) -> None:
    terminals(stdin=True, stdout=True)
    assert_exception_function(
        subtests,
        lambda system: collect_profile_keys(_args(system)),
        invalid_params=("nothing",),
        valid_params=("python",),
        exception_type=ParamError,
        error_name="EXTRACTOR_CONFIG_INVALID",
        label="system",
        value="nothing",
        problem="No profile is registered for the system 'nothing'.",
        expected="One of the registered systems: generic, python.",
        verbose=False,
    )
    # only the valid system got as far as the question about profiles
    assert prompts.profile_questions
    assert all(question == ("Profiles", {"a": "Alpha", "b": "Beta"}) for question in prompts.profile_questions)


def test_an_unknown_system_given_by_the_answer_is_refused_too(prompts, terminals) -> None:
    terminals(stdin=True, stdout=True)
    prompts.system_answer = "nothing"
    with pytest.raises(ParamError):
        collect_profile_keys(_args())
