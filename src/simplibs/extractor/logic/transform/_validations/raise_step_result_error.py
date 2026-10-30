from typing import Any, NoReturn
from simplibs.exception import OperationError


def raise_step_result_error(
    step: Any,
    result: Any,
) -> NoReturn:
    """Raise OperationError when a transformation step does not return text.

    Args:
        step: The step (an `Action`) that was applied.
        result: What it returned instead of a string.
    """

    # 1. Raise structured OperationError wrapping a TypeError
    raise OperationError(
        error_name="EXTRACTOR_STEP_RESULT_INVALID",
        label=f"result of step {type(step).__name__}",
        value=result,
        problem=f"The step returned {type(result).__name__}, not str.",
        expected="A text: every step of a profile takes a str and returns a str.",
        how_to_fix=(
            "Make the step return the transformed text.",
            "Check the order of the steps: each one receives the text the previous one returned.",
        ),
        exception=TypeError,
    )


_DESIGN_NOTES = """
# raise_step_result_error — A Step Must Keep the Text a Text

## Purpose
Steps are `Action`s, which may return anything. The render phase needs a
string. Failing at the step names the culprit; failing later in the renderer
would blame the output.

## Not a Config Error
The profile is valid; one of its steps misbehaves on one file. The run
therefore reports that file as failed and carries on.
"""
