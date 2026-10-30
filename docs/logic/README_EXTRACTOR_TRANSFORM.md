# 🧹 `logic/transform` — Phase 3: Clean the Text

The third phase runs the **steps of the profile** on the text the [read phase](README_EXTRACTOR_READ.md)
returned — strips comments, squeezes blank lines, whatever the profile says. One file at a time, text in, text
out.

```
text ──► steps_for(steps, suffix) ──► an Action, or None ──► Action(text) ──► text
              which pipeline?                                   run it          still a str
```

The steps of a profile are `Action` objects of [`simplibs-actions`](https://pypi.org/project/simplibs-actions/),
chained with `>>`. A profile may hold one pipeline for every file, one pipeline per suffix, or none — see
[`StepsSpec`](../README_EXTRACTOR_ANNOTATIONS.md#stepsspec).

```python
from simplibs.actions import to_action
from simplibs.extractor.logic import apply_steps

@to_action
def upper(data: str) -> str:
    return data.upper()

apply_steps("hello", upper(), ".py")                    # -> 'HELLO'
apply_steps("hello", None, ".py")                       # -> 'hello'          no steps: the text stays as it is
```

**A step sees only the text.** It never receives the path. A pipeline that must clean Python differently from
JavaScript is therefore chosen by the **suffix mapping** of the profile *before* the step runs — that is why
`StepsSpec` has a mapping form.

**A step must return a string.** The render phase needs a string; a step that returns something else is
refused on the spot, so the culprit is the step and not the output.

**A failing step ruins one file, not the run.** `apply_steps` does not wrap what a step raises. The loop of the
run catches it, marks **that file** as `error` (reason `transform failed: …`) and goes on with the next one;
the run is then unsuccessful.

```python
# the loop body of extract(), shortened — the one broad `except` of the library: the steps are somebody else's code
try:
    output = apply_steps(text, profile.steps, path.suffix)
except Exception as exc:
    failed = dataclasses.replace(report, status="error", reason=f"transform failed: {describe_failure(exc)}")
    return failed, None
```

## What is public

Both functions are declared in the `__all__` of `simplibs.extractor.logic` and are **not** exported from the package root.
Your programs call `extract()`; these two are documented for readers who want to know what a profile's
steps do, for tools built on the extractor and for tests.

| Function      | What it does                                                         | Used by                        |
|---------------|----------------------------------------------------------------------|--------------------------------|
| `apply_steps` | runs the steps that apply to a file's suffix on its text             | the loop of `extract`          |
| `steps_for`   | picks the action for a suffix out of a `StepsSpec`                   | `apply_steps`                  |

---

## 🧭 Table of Contents

* [`apply_steps`](#apply_steps)
* [`steps_for`](#steps_for)

[⬅️ Back to main README](../../README.md#-the-six-phases)

---

### `apply_steps`

**Transforms the text of one file** with the steps that apply to its suffix.

**Parameters:**

| Name     | Type        | Description                                                   |
|----------|-------------|---------------------------------------------------------------|
| `text`   | `str`       | The text of the file.                                         |
| `steps`  | `StepsSpec` | The profile's steps: `None`, one `Action`, or a mapping `suffix -> Action`. |
| `suffix` | `str`       | The suffix of the file (`".py"`); the case is ignored.        |

**Returns:** the transformed `str`; the **original text** if no step applies.

**Raises:**
`OperationError` (`EXTRACTOR_STEP_RESULT_INVALID`) — the step returned something that is not a string.
Any error the step itself raises is passed on unchanged; the caller reports it for this file.

**Example usage:**

```python
from simplibs.actions import to_action
from simplibs.extractor.logic import apply_steps

@to_action
def strip(data: str) -> str:
    return data.strip()

@to_action
def upper(data: str) -> str:
    return data.upper()

@to_action
def count_lines(data: str) -> int:                      # a step that returns a number — a mistake
    return len(data.splitlines())

# 1. One action for every file
apply_steps("  hello  ", strip() >> upper(), ".py")     # -> 'HELLO'
apply_steps("  hello  ", strip() >> upper(), ".md")     # -> 'HELLO'

# 2. One action per suffix; "*" is the fallback
steps = {".py": strip() >> upper(), "*": strip()}
apply_steps("  hello  ", steps, ".py")                  # -> 'HELLO'
apply_steps("  hello  ", steps, ".PY")                  # -> 'HELLO'       the case of the suffix is ignored
apply_steps("  hello  ", steps, ".md")                  # -> 'hello'       the fallback

# 3. Nothing applies — the text is returned as it is
apply_steps("  hello  ", None, ".py")                   # -> '  hello  '
apply_steps("  hello  ", {".py": upper()}, ".md")       # -> '  hello  '   no key for .md and no "*"

# 4. A step that does not return text
apply_steps("hello", count_lines(), ".py")              # raises OperationError — the step returned int, not str
```

A profile is also checked when it is built (`EXTRACTOR_PROFILE_INVALID`), but the type of what a step
**returns** can be seen only when it runs — which is why this check lives here.

**Why the type check.** Steps are `Action`s, which may return anything, while the render phase needs a
string. Failing at the step names the culprit; failing later in the renderer would blame the output.

**Why errors are not wrapped.** The loop reports a failing step against the file it failed on and
continues. Wrapping the error here would only hide the step's own card.

<details>
<summary>🔍 Under the hood</summary>

```python
def apply_steps(
    text: str,
    steps: StepsSpec,
    suffix: str,
) -> str:

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
```

The card of the type error:

```python
def raise_step_result_error(step: Any, result: Any) -> NoReturn:
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
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `steps_for`

**Picks the action that applies to a file suffix** — the one place that understands the three shapes of
`StepsSpec`.

**Parameters:**

| Name     | Type        | Description                                                   |
|----------|-------------|---------------------------------------------------------------|
| `steps`  | `StepsSpec` | The profile's steps.                                          |
| `suffix` | `str`       | The suffix of the file (`".py"`); the case is ignored.        |

**Returns:** the `Action` that applies, or `None` if the text stays as it is.

**Example usage:**

```python
from simplibs.actions import to_action
from simplibs.extractor.logic import steps_for

@to_action
def upper(data: str) -> str:
    return data.upper()

@to_action
def strip(data: str) -> str:
    return data.strip()

clean_py, clean_other = upper(), strip()

steps_for(None, ".py")                                  # -> None            no steps
steps_for(clean_py, ".py") is clean_py                  # -> True            one action: the same for every file
steps_for(clean_py, "") is clean_py                     # -> True            ... even for a file without a suffix

steps = {".py": clean_py, "*": clean_other}
steps_for(steps, ".py") is clean_py                     # -> True            the file's own suffix
steps_for(steps, ".PY") is clean_py                     # -> True            the case is ignored
steps_for(steps, ".md") is clean_other                  # -> True            the fallback "*"
steps_for({".py": clean_py}, ".md")                     # -> None            no key and no fallback
```

**The shapes** — one question, three answers:

| `steps`               | Answer for a suffix                                                        |
|-----------------------|----------------------------------------------------------------------------|
| `None`                | `None`                                                                     |
| one `Action`          | that action, whatever the suffix                                           |
| `{suffix: Action}`    | the action of the suffix, else the one of `"*"`, else `None`               |

**Why the case is ignored.** The keys of a profile's mapping must be lowercase — that is checked when the
profile is built — so the suffix of the file is lowercased for the lookup.

**Why a separate function.** The caller asks *"what applies to `.py`?"* and gets an action or nothing. How the
profile stores its steps stays a secret of this function, so a fourth shape of `StepsSpec` would change one
place.

<details>
<summary>🔍 Under the hood</summary>

```python
def steps_for(steps: StepsSpec, suffix: str) -> Action | None:

    # 1. No steps at all
    if steps is None:
        return None

    # 2. A mapping: the file's own suffix, otherwise the fallback "*"
    if isinstance(steps, Mapping):
        return steps.get(suffix.lower(), steps.get("*"))

    # 3. One action for every file
    return steps
```

</details>

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../../README.md#-the-six-phases)
