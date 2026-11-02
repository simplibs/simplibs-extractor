from collections.abc import Mapping, Sequence
from typing import Any
# Outers
from ..definitions import Profile
# Inners
from .asserts import assert_profile_identity, assert_profile_selection, assert_profile_steps


def assert_profile(
    subtests: Any,
    profile: Profile,
    *,
    expected_key: str,
    expected_output_name: str | None = None,
    expected_format: str | None = None,
    expected_description: str | None = None,
    included: Sequence[str] = (),
    excluded: Sequence[str] = (),
    step_cases: Mapping[str, Sequence[tuple[str, str]]] | None = None,
    unchanged_suffixes: Sequence[str] = (),
    cover_all_suffixes: bool = False,
    verbose: bool = True,
    intro: str = "",
) -> None:
    """Master orchestrator for testing a profile of the extractor.

    Checks what a profile promises: how it is called and what it writes, which
    files it takes, and what its steps do to a text. Everything is fed as data,
    so one call replaces the test module a hand-written profile test would need.
    Anything beyond it (a long realistic file and its exact result, a run over a
    folder) is a focused test beside this call.

    Args:
        subtests: The native pytest subtests fixture manager instance.
        profile: The Profile under test.
        expected_key: The registry key (`"python/code-clean"`).
        expected_output_name: If provided, `profile.output_name` must equal it.
        expected_format: If provided, `profile.format` must equal it.
        expected_description: If provided, `profile.description` must equal it exactly.
            Without it, only the generic contract is checked (one non-blank line).
        included: Paths relative to the source (`"pkg/a.py"`) that the profile must take.
        excluded: Relative paths that the profile must leave out.
        step_cases: `{suffix: [(text, expected_text), ...]}` for the steps.
        unchanged_suffixes: Suffixes for which no step may apply.
        cover_all_suffixes: If True, every suffix key of the steps must have a case.
        verbose: Enables isolated pytest subtest tracking for every check.
        intro: Optional prefix for generated subtest names (derived from the key when left empty).

    Example:
        assert_profile(
            subtests, PYTHON_SRC_CLEAN,
            expected_key="python/src-clean",
            expected_output_name="python_src_clean.md",
            included=("pkg/a.py", "pkg/__init__.py"),
            excluded=("tests/test_a.py", ".venv/x.py", "setup.cfg"),
            step_cases={".py": [("# c\\nx = 1\\n", "x = 1\\n")]},
            unchanged_suffixes=(".txt",),
        )
    """
    assert isinstance(profile, Profile), (
        f"assert_profile expects a Profile instance, got {type(profile).__name__}."
    )

    prefix = f"{intro}[{profile.key}] " if intro == "" else f"{intro} "

    # 1. Name tags: key, description, output name, format
    assert_profile_identity(
        subtests,
        profile,
        expected_key=expected_key,
        expected_output_name=expected_output_name,
        expected_format=expected_format,
        expected_description=expected_description,
        verbose=verbose,
        intro=prefix,
    )

    # 2. Which files it takes
    if included or excluded:
        assert_profile_selection(
            subtests,
            profile,
            included,
            excluded,
            verbose=verbose,
            intro=prefix,
        )

    # 3. What its steps do
    if step_cases or unchanged_suffixes or cover_all_suffixes:
        assert_profile_steps(
            subtests,
            profile,
            step_cases or {},
            unchanged_suffixes,
            cover_all_suffixes=cover_all_suffixes,
            verbose=verbose,
            intro=prefix,
        )


_DESIGN_NOTES = """
# assert_profile (Master Profile Orchestrator)

## Purpose
The single entry point for testing a `Profile`, built like
`assert_rule_contract`: one call fed with data, three blades behind it.
Meant for the add-ons of the extractor, which are made of profiles.

---

## 1. Contract Coverage

1. **Identity** (`assert_profile_identity`) — always: the key, a one-line
   description; the output name, format and exact description when given.
2. **Selection** (`assert_profile_selection`) — when `included` or `excluded`
   is given: which relative paths the rules take.
3. **Steps** (`assert_profile_steps`) — when `step_cases`, `unchanged_suffixes`
   or `cover_all_suffixes` is given: what the steps do to a text.

Blades 2 and 3 run only when there is data for them, because a profile with
no rules and no steps (`generic/all`) has nothing to ask. A profile that has
rules and is called without paths is not refused: how much to pin down is the
decision of the test, `cover_all_suffixes` being the way to make it strict.

---

## 2. Design Choices

* **Fail-Fast Type Guard:**
  `isinstance(profile, Profile)` before any blade, as in `assert_rule_contract`.
* **No Wrapping Subtest:**
  Each blade opens a subtest per value. The prefix (`[python/src-clean] `)
  passed down as `intro` groups them in the report; an outer subtest would
  never see a failure of an inner one.
* **The Key as the Group Name:**
  A profile has its key, so the report reads `[python/src-clean] test_selected_...`
  without the caller naming anything.
* **`expected_` Names:**
  `output_name` and `format` would shadow nothing here but would read as
  values to set; the `expected_` prefix is the one the rules testing tools use.

---

## 3. Scope Boundary — What This Does NOT Do

* Registration (`get_profile(key) is profile` after `register_all`) is the test
  of the add-on's plugin, once for all of its profiles.
* Whether the output format is registered is checked by the run itself; a
  custom format is registered by the add-on, not by the profile.
* A run over real files, with the rules of a config added, is an integration
  test.
"""
