from .apply_steps import apply_steps
from .by_suffix import by_suffix
from .steps_for import steps_for


_DESIGN_NOTES = """
# logic/transform — Phase 3: Clean the Text

Plain imports, no `__all__`.

## Internal Components Registry

| Component     | Type     | Description                                          |
| :------------ | :------- | :--------------------------------------------------- |
| `apply_steps` | Function | Runs the steps that apply to a file's suffix.        |
| `by_suffix`   | Function | Gives one step to a list of suffixes.                |
| `steps_for`   | Function | Picks the action for a suffix out of a `StepsSpec`.  |
"""
