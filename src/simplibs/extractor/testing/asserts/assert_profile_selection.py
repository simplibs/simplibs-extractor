from collections.abc import Sequence
from pathlib import Path
from typing import Any
from simplibs.exception.testing import maybe_subtest
# Outers
from ...definitions import Profile


def assert_profile_selection(
    subtests: Any,
    profile: Profile,
    included: Sequence[str],
    excluded: Sequence[str],
    *,
    verbose: bool = True,
    intro: str = "",
) -> None:
    """Verify which relative paths the include and exclude rules of a profile take.

    A file is taken when `include` accepts it (or there is no `include`) and
    `exclude` does not match it (or there is no `exclude`), the same as in the
    select phase of the extractor.

    Args:
        subtests: The native pytest subtests fixture manager instance.
        profile: The Profile under test.
        included: Paths relative to the source folder (`"pkg/a.py"`, written with `/`)
            that the profile must take.
        excluded: Paths that the profile must leave out, whichever rule does it.
        verbose: Enables isolated pytest subtest tracking for each checked path.
        intro: Optional prefix string added to generated subtest identity names.
    """
    assert isinstance(profile, Profile), (
        f"assert_profile_selection expects a Profile instance, got {type(profile).__name__}."
    )
    overlap = sorted(set(included) & set(excluded))
    assert not overlap, (
        f"assert_profile_selection received paths that are both included and excluded: {overlap}."
    )

    def why_left_out(path: str) -> str | None:
        """The reason the profile does not take the path; None if it takes it."""
        relative = Path(path)
        if profile.include is not None and not profile.include(relative):
            return "the include rule does not accept it"
        if profile.exclude is not None and profile.exclude(relative):
            return "the exclude rule matches it"
        return None

    # 1. Paths the profile must take
    for index, path in enumerate(included):
        with maybe_subtest(
            subtests,
            name=f"{intro}test_selected_#index_{index}_{path}",
            verbose=verbose,
        ):
            reason = why_left_out(path)
            assert reason is None, f"Expected {path!r} to be taken, but {reason}."

    # 2. Paths the profile must leave out
    for index, path in enumerate(excluded):
        with maybe_subtest(
            subtests,
            name=f"{intro}test_left_out_#index_{index}_{path}",
            verbose=verbose,
        ):
            assert why_left_out(path) is not None, (
                f"Expected {path!r} to be left out, but the profile takes it."
            )


_DESIGN_NOTES = """
# assert_profile_selection (File Choice Blade)

## Purpose
A profile is, first of all, a decision about files. This blade asks it the
way the select phase does: with the path relative to the source folder.

---

## 1. Execution Rationale

* **Relative Paths as Text:**
  The caller writes `"tests/test_a.py"`; the blade makes a `Path` of it, the
  type the rules receive in a real run. Rules that look at parent folders or
  the name therefore see what they would see there.
* **The Reason Is Part of the Message:**
  A failure says whether the `include` rule did not accept the path or the
  `exclude` rule matched it, so the right rule is looked at first.
* **`exclude` Beats `include`:**
  A path of `excluded` fails only if the profile takes it; it does not matter
  which rule leaves it out. A test of a path that every rule accepts and the
  `exclude` rejects is the most common one and the one most easily forgotten.
* **Overlap Is a Mistake of the Test:**
  A path in both lists could never pass, so the call fails at once and says so.

---

## 2. Scope Boundary

The two conditions are written here again (three lines) because the select
phase has no function that answers for one path without a folder on the disk.
A run over real files, with the config's rules on top, belongs to the
integration tests of the add-on.
"""
