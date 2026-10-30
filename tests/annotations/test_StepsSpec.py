from collections.abc import Mapping
from types import MappingProxyType
import pytest
from simplibs.rules import IsTyping
from simplibs.actions import Action
from simplibs.extractor.annotations import StepsSpec


class DummyAction(Action):
    """A minimal mock action for testing StepsSpec validity."""

    def __call__(self, text: str) -> str:
        return text

    def run(self, text: str) -> str:
        return text


@pytest.mark.parametrize(
    "value",
    [
        None,
        DummyAction(),
        {},
        {"*": DummyAction()},
        {".py": DummyAction(), "*": DummyAction()},
        MappingProxyType({".py": DummyAction()}),
    ],
)
def test_steps_spec_accepts_valid_specifications(value) -> None:
    """None, a single Action, or any mapping of suffix to Action are accepted."""
    assert IsTyping(StepsSpec).is_valid(value)


@pytest.mark.parametrize(
    "value",
    [
        "not-an-action",
        123,
        {123: DummyAction()},  # non-string key
        {".py": "not-an-action"},  # non-action value
        [DummyAction()],  # list instead of mapping or single action
        DummyAction,  # the class itself, not an instance
    ],
)
def test_steps_spec_rejects_everything_else(value) -> None:
    """Invalid action types, wrong mapping keys/values, lists and bare classes are rejected."""
    assert not IsTyping(StepsSpec).is_valid(value)


def test_steps_spec_does_not_judge_the_shape_of_the_keys() -> None:
    """The shape of a key ('.PY', 'py') is not the type's job - Profile checks it when it is built."""
    assert IsTyping(StepsSpec).is_valid({".PY": DummyAction(), "py": DummyAction()})
