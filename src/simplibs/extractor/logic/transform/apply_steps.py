# Outers
from ...annotations import StepsSpec
# Inners
from .steps_for import steps_for
from ._validations import raise_step_result_error


def apply_steps(
    text: str,
    steps: StepsSpec,
    suffix: str,
) -> str:
    """Transform the text of one file with the steps that apply to its suffix.

    Args:
        text: The text of the file.
        steps: The profile's steps (see `StepsSpec`).
        suffix: The suffix of the file (`".py"`).

    Returns:
        The transformed text; the original if no step applies.

    Raises:
        OperationError: If the step returns something that is not a string.
        Any error the step itself raises is passed on unchanged; the caller reports it for this file.
    """

    # 1. Choose the action for this file
    step = steps_for(steps, suffix)
    if step is None:
        return text

    # 2. Run it
    result = step(text)

    # 3. A step must keep the text a text
    if not isinstance(result, str):
        raise_step_result_error(step, result)

    return result


_DESIGN_NOTES = """
# apply_steps — Run the Profile's Pipeline on One Text

## Purpose
The whole transform phase for one file: choose, run, check the type.

## The Step Knows Only the Text
It never sees the path. Language-specific cleaning is chosen by the suffix
mapping *before* the call, which is why `StepsSpec` has the mapping form.

## Errors Are Passed On
A step that raises is not wrapped here. The run loop reports it against the
file it failed on and continues; wrapping it would only hide the step's own
card.
"""
