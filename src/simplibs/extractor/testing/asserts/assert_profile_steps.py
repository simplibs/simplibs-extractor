from collections.abc import Mapping, Sequence
from typing import Any
from simplibs.exception.testing import maybe_subtest
# Outers
from ...definitions import Profile
from ...definitions._helpers import is_suffix_key
from ...logic import apply_steps, steps_for


def assert_profile_steps(
    subtests: Any,
    profile: Profile,
    cases: Mapping[str, Sequence[tuple[str, str]]],
    unchanged_suffixes: Sequence[str] = (),
    *,
    cover_all_suffixes: bool = False,
    verbose: bool = True,
    intro: str = "",
) -> None:
    """Verify what the steps of a profile do to a text, suffix by suffix.

    The steps are run by the same functions as in a real extraction, so the
    choice of the action (own suffix, fallback `"*"`, one action for all)
    is the one a run would make.

    Args:
        subtests: The native pytest subtests fixture manager instance.
        profile: The Profile under test.
        cases: `{suffix: [(text, expected_text), ...]}`; the suffix is a file suffix
            (`".py"`), never `"*"`. To test the fallback, use a suffix that no key names.
        unchanged_suffixes: Suffixes for which no step may apply at all (the text stays as it is).
        cover_all_suffixes: If True, every suffix key of a mapping of steps must have
            a case, and the fallback `"*"` needs a case with a suffix that no key names.
        verbose: Enables isolated pytest subtest tracking for each check.
        intro: Optional prefix string added to generated subtest identity names.
    """
    assert isinstance(profile, Profile), (
        f"assert_profile_steps expects a Profile instance, got {type(profile).__name__}."
    )
    for suffix in (*cases, *unchanged_suffixes):
        assert is_suffix_key(suffix) and suffix != "*", (
            f"assert_profile_steps expects file suffixes such as '.py' (lowercase), got {suffix!r}."
        )
    both = sorted(set(cases) & set(unchanged_suffixes))
    assert not both, (
        f"assert_profile_steps received suffixes that have cases and are also unchanged: {both}."
    )

    # 1. What the steps do to a text
    for suffix, pairs in cases.items():
        for index, (text, expected) in enumerate(pairs):
            with maybe_subtest(
                subtests,
                name=f"{intro}test_steps_{suffix}_#index_{index}",
                verbose=verbose,
            ):
                result = apply_steps(text, profile.steps, suffix)
                assert result == expected, (
                    f"Expected the steps for {suffix!r} to turn {text!r} into {expected!r}, got {result!r}."
                )

    # 2. Suffixes that no step touches
    for index, suffix in enumerate(unchanged_suffixes):
        with maybe_subtest(
            subtests,
            name=f"{intro}test_no_step_#index_{index}_{suffix}",
            verbose=verbose,
        ):
            step = steps_for(profile.steps, suffix)
            assert step is None, (
                f"Expected no step for {suffix!r}, but the profile applies {type(step).__name__}."
            )

    # 3. Nothing left untested (opt-in)
    if cover_all_suffixes and isinstance(profile.steps, Mapping):
        with maybe_subtest(
            subtests,
            name=f"{intro}test_every_suffix_has_a_case",
            verbose=verbose,
        ):
            keys = [key for key in profile.steps if key != "*"]
            missing = sorted(set(keys) - set(cases))
            assert not missing, f"The steps have suffixes without a case: {missing}."
            if "*" in profile.steps:
                assert set(cases) - set(keys), (
                    "The fallback '*' has no case: add a suffix that no key names (for example '.xyz')."
                )


_DESIGN_NOTES = """
# assert_profile_steps (Text Transformation Blade)

## Purpose
Shows what a profile does to the text of a file. The data is a table of
`(text, expected_text)` pairs per suffix, so the test reads as a list of
examples.

---

## 1. Execution Rationale

* **The Extractor's Own Functions:**
  The blade calls `apply_steps` and `steps_for`, the functions the transform
  phase uses. It does not look into the mapping itself, so a change in how a
  suffix is resolved (case, fallback, a new kind of mapping) is followed
  without a change here, and cannot make the test agree with a wrong profile.
* **`unchanged_suffixes` Checks the Choice, Not the Result:**
  `steps_for(...) is None` says that no step applies. A pair whose expected
  text equals the input would also be green when a step existed and did nothing.
* **`cover_all_suffixes` Is Opt-In:**
  A profile that maps every suffix of a language to the same action would
  need a case for each; the person decides whether that is wanted. When it
  is, a suffix added to the profile later and never tested fails here.
* **Only Real Suffixes:**
  Keys such as `"*"` or `".PY"` can never be the suffix of a file. Using one in
  a case is a mistake of the test and fails at once with the reason.

---

## 2. Scope Boundary

One text at a time, steps only. How a failing step is reported against its
file is a matter of the run (`process_source`).
"""
