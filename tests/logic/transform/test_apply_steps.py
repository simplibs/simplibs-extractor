from pathlib import Path
import pytest
from simplibs.exception import NotFoundError, OperationError
from simplibs.exception.testing import assert_exception_function
from simplibs.extractor.logic.select._validations import raise_source_not_found_error
from simplibs.extractor.logic.transform import apply_steps


# ---------------------------------------------------------------- no step, one step, a mapping

def test_no_steps_keep_the_text() -> None:
    text = "Hello\n"
    assert apply_steps(text, None, ".py") is text


def test_one_action_transforms_the_text(make_action) -> None:
    assert apply_steps("abc", make_action(str.upper), ".py") == "ABC"
    assert apply_steps("abc", make_action(str.upper), "") == "ABC"


def test_mapping_applies_the_action_of_the_suffix(make_action) -> None:
    steps = {".py": make_action(str.upper), ".md": make_action(str.lower)}
    assert apply_steps("Ab", steps, ".py") == "AB"
    assert apply_steps("Ab", steps, ".md") == "ab"


def test_a_suffix_without_an_action_keeps_the_text(make_action) -> None:
    text = "Ab"
    assert apply_steps(text, {".py": make_action(str.upper)}, ".txt") is text


def test_the_fallback_is_applied_to_other_suffixes(make_action) -> None:
    steps = {".py": make_action(str.upper), "*": make_action(str.lower)}
    assert apply_steps("Ab", steps, ".txt") == "ab"
    assert apply_steps("Ab", steps, ".py") == "AB"


def test_suffix_case_is_ignored(make_action) -> None:
    assert apply_steps("ab", {".py": make_action(str.upper)}, ".PY") == "AB"


def test_an_empty_text_is_passed_to_the_step(make_action) -> None:
    seen: list[str] = []

    def step(text):
        seen.append(text)
        return text + "!"

    assert apply_steps("", make_action(step), ".py") == "!"
    assert seen == [""]


def test_the_step_gets_the_text_exactly_once_and_unchanged(make_action) -> None:
    seen: list[str] = []

    def step(text):
        seen.append(text)
        return text

    text = "line 1\r\nline 2\n\tPříliš žluťoučký kůň\n"
    assert apply_steps(text, make_action(step), ".txt") == text
    assert seen == [text]


def test_the_step_may_return_an_empty_text(make_action) -> None:
    assert apply_steps("abc", make_action(lambda text: ""), ".py") == ""


def test_the_result_of_the_step_is_returned_as_it_is(make_action) -> None:
    result = "new text"
    assert apply_steps("old", make_action(lambda text: result), ".py") is result


# ---------------------------------------------------------------- a step that does not return text

@pytest.mark.parametrize("result", [5, None, b"bytes", ["a"], 1.5, ("a",)])
def test_a_result_that_is_not_text_gives_a_step_result_card(subtests, make_action, result) -> None:
    action = make_action(lambda text: result, name="Broken")
    assert_exception_function(
        subtests,
        lambda: apply_steps("x", action, ".py"),
        invalid_params=(),
        exception_type=OperationError,
        error_name="EXTRACTOR_STEP_RESULT_INVALID",
        label="result of step Broken",
        value=result,
        problem=f"The step returned {type(result).__name__}, not str.",
        exception=TypeError,
        verbose=False,
    )


def test_the_result_is_checked_for_the_step_that_was_chosen(make_action) -> None:
    """A broken step for another suffix is never run, so it cannot spoil this file."""
    steps = {".py": make_action(lambda text: 5, name="Broken"), ".md": make_action(str.upper)}
    assert apply_steps("ab", steps, ".md") == "AB"


# ---------------------------------------------------------------- errors of the step itself

def test_an_error_of_the_step_is_passed_on_unchanged(make_action) -> None:
    error = RuntimeError("boom")

    def step(text):
        raise error

    with pytest.raises(RuntimeError) as caught:
        apply_steps("x", make_action(step), ".py")
    assert caught.value is error


def test_a_card_of_the_step_is_not_wrapped(make_action) -> None:
    """The run loop reports the step's own card for the file; wrapping it would only hide it."""

    def step(text):
        raise_source_not_found_error(Path("missing"))

    with pytest.raises(NotFoundError) as caught:
        apply_steps("x", make_action(step), ".py")
    assert caught.value.error_name == "EXTRACTOR_SOURCE_NOT_FOUND"
