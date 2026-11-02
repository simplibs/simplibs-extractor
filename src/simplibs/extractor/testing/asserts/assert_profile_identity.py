from typing import Any
from simplibs.exception.testing import maybe_subtest
# Outers
from ...definitions import Profile


def assert_profile_identity(
    subtests: Any,
    profile: Profile,
    *,
    expected_key: str,
    expected_output_name: str | None = None,
    expected_format: str | None = None,
    expected_description: str | None = None,
    verbose: bool = True,
    intro: str = "",
) -> None:
    """Verify the name tags of a profile: what it is called and what it writes.

    Args:
        subtests: The native pytest subtests fixture manager instance.
        profile: The Profile under test.
        expected_key: The registry key (`"python/code-clean"`).
        expected_output_name: If provided, `profile.output_name` must equal it.
        expected_format: If provided, `profile.format` must equal it.
        expected_description: If provided, `profile.description` must equal it exactly.
            Without it, only the generic contract is checked (one non-blank line).
        verbose: Enables isolated pytest subtest tracking for each check.
        intro: Optional prefix string added to generated subtest identity names.
    """
    assert isinstance(profile, Profile), (
        f"assert_profile_identity expects a Profile instance, got {type(profile).__name__}."
    )

    # 1. The key
    with maybe_subtest(
        subtests,
        name=f"{intro}test_key",
        verbose=verbose,
    ):
        assert profile.key == expected_key, (
            f"Expected the key {expected_key!r}, got {profile.key!r}."
        )

    # 2. The description: shown by the listing commands, so one non-blank line
    with maybe_subtest(
        subtests,
        name=f"{intro}test_description_is_one_line",
        verbose=verbose,
    ):
        description = profile.description
        assert isinstance(description, str) and description.strip() != "", (
            f"Expected a non-blank description (the listing commands show it), got {description!r}."
        )
        assert "\n" not in description.strip(), (
            f"Expected a one-line description, got {description!r}."
        )

    # 3. The optional exact values
    if expected_description is not None:
        with maybe_subtest(
            subtests,
            name=f"{intro}test_description_expected_text",
            verbose=verbose,
        ):
            assert profile.description == expected_description, (
                f"Expected the description {expected_description!r}, got {profile.description!r}."
            )

    if expected_output_name is not None:
        with maybe_subtest(
            subtests,
            name=f"{intro}test_output_name",
            verbose=verbose,
        ):
            assert profile.output_name == expected_output_name, (
                f"Expected the output name {expected_output_name!r}, got {profile.output_name!r}."
            )

    if expected_format is not None:
        with maybe_subtest(
            subtests,
            name=f"{intro}test_format",
            verbose=verbose,
        ):
            assert profile.format == expected_format, (
                f"Expected the format {expected_format!r}, got {profile.format!r}."
            )


_DESIGN_NOTES = """
# assert_profile_identity (Name Tag Blade)

## Purpose
Checks what a person sees of a profile before it runs: its key, the line in
`--list-profiles`, the name of the file it writes and the format.

---

## 1. Execution Rationale

* **Fail-Fast Type Guard:**
  `isinstance(profile, Profile)` first, so passing a key string or a class
  gives one clear message instead of an `AttributeError` in a subtest.
* **The Description Contract Always Runs:**
  `Profile` allows an empty description (the default), but a profile that is
  listed with an empty line is a profile nobody can choose. So a non-blank,
  one-line description is the generic contract; the exact text is opt-in,
  as with `describe()` of a rule.
* **Pinned Values Are Opt-In:**
  `expected_output_name` and `expected_format` are compared only when given.
  A profile that keeps the defaults can leave them out; one that names its
  output (`python_src_clean.md`) should pin it, because a rename changes what
  people find on their disk.

---

## 2. Scope Boundary

Whether the key part is usable, whether the output name is portable and
whether the format has the right shape is checked when a `Profile` is built
(see `Profile`). Whether the format is registered is a matter of the add-on's
registration and belongs to its plugin test.
"""
