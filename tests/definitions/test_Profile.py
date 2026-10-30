from dataclasses import FrozenInstanceError, replace
import pytest
from simplibs.exception import ParamError, ValidationError
from simplibs.exception.testing import assert_exception_function
from simplibs.rules import IsTyping
from simplibs.extractor.constants import DEFAULT_OUTPUT_NAME
from simplibs.extractor.definitions import Profile


# ---------------------------------------------------------------- defaults and key

def test_defaults() -> None:
    """Only `system` and `name` are required."""
    profile = Profile("python", "code-clean")
    assert profile.description == ""
    assert profile.include is None
    assert profile.exclude is None
    assert profile.steps is None
    assert profile.output_name == DEFAULT_OUTPUT_NAME
    assert profile.format == "markdown"


@pytest.mark.parametrize(
    "system, name, key",
    [
        ("python", "code-clean", "python/code-clean"),
        ("generic", "all", "generic/all"),
        ("web", "css3", "web/css3"),
    ],
)
def test_key_is_system_slash_name(system, name, key) -> None:
    assert Profile(system, name).key == key


def test_accepts_every_field(dummy_action) -> None:
    rule = IsTyping(str)
    profile = Profile(
        system="python",
        name="code-clean",
        description="Python without comments",
        include=rule,
        exclude=rule,
        steps={".py": dummy_action, "*": dummy_action},
        output_name="code.txt",
        format="plain",
    )
    assert profile.include is rule and profile.exclude is rule
    assert profile.output_name == "code.txt"
    assert profile.format == "plain"


@pytest.mark.parametrize("steps_kind", ["none", "single", "mapping", "fallback_only", "empty_mapping"])
def test_accepts_every_shape_of_steps(dummy_action, steps_kind) -> None:
    steps = {
        "none": None,
        "single": dummy_action,
        "mapping": {".py": dummy_action},
        "fallback_only": {"*": dummy_action},
        "empty_mapping": {},
    }[steps_kind]
    assert Profile("python", "x", steps=steps).steps == steps


@pytest.mark.parametrize("output_name", ["out.md", "extraction.txt", "report (1).md", "výstup.md", "no_suffix"])
def test_accepts_portable_output_names(output_name) -> None:
    assert Profile("python", "x", output_name=output_name).output_name == output_name


# ---------------------------------------------------------------- the key parts (card)

def _build_with(field: str, value: str) -> Profile:
    parts = {"system": "python", "name": "code-clean", field: value}
    return Profile(**parts)


@pytest.mark.parametrize("field", ["system", "name"])
@pytest.mark.parametrize("value", ["", "   ", "a/b", "a,b", "a b", " a", "a "])
def test_unusable_key_part_gives_a_profile_invalid_card(subtests, field, value) -> None:
    """A key part with a separator, whitespace or nothing at all fails when the profile is built."""
    expected = f"a non-blank {field} without '/', ',' or whitespace"
    assert_exception_function(
        subtests,
        _build_with,
        invalid_params=(field, value),
        valid_params=(field, "python"),
        exception_type=ParamError,
        error_name="EXTRACTOR_PROFILE_INVALID",
        label=f"profile {field}",
        value=value,
        problem=f"The {field} {value!r} cannot be a part of a profile key.",
        expected=expected,
        verbose=False,
    )


@pytest.mark.parametrize("field", ["system", "name"])
@pytest.mark.parametrize("value", [None, 5, b"python", ["python"]])
def test_non_string_key_part_is_rejected_by_the_type_layer(field, value) -> None:
    """A wrong type never reaches the character check - validation catches it first."""
    with pytest.raises(ValidationError):
        _build_with(field, value)


# ---------------------------------------------------------------- output name (card)

@pytest.mark.parametrize("output_name", ["a/b.md", "../x.md", "sub/extraction.md", ""])
def test_unusable_output_name_gives_a_profile_invalid_card(subtests, output_name) -> None:
    """An output name must be a plain file name, never a path."""
    assert_exception_function(
        subtests,
        lambda value: Profile("python", "x", output_name=value),
        invalid_params=(output_name,),
        valid_params=("ok.md",),
        exception_type=ParamError,
        error_name="EXTRACTOR_PROFILE_INVALID",
        label="profile output_name",
        value=output_name,
        problem=f"The output name {output_name!r} is not a usable file name.",
        expected="a portable file name (no path separators or forbidden characters)",
        verbose=False,
    )


@pytest.mark.parametrize("output_name", [None, 5, b"a.md"])
def test_non_string_output_name_is_rejected_by_the_type_layer(output_name) -> None:
    with pytest.raises(ValidationError):
        Profile("python", "x", output_name=output_name)


# ---------------------------------------------------------------- steps mapping keys (card)

@pytest.mark.parametrize("key", ["py", ".PY", ".Py", ".", "", "*.py", " .py"])
def test_unusable_steps_key_gives_a_profile_invalid_card(subtests, dummy_action, key) -> None:
    """A key that can never match a file suffix is rejected at build time, not silently ignored on every run."""
    assert_exception_function(
        subtests,
        lambda value: Profile("python", "x", steps={value: dummy_action}),
        invalid_params=(key,),
        valid_params=(".py",),
        exception_type=ParamError,
        error_name="EXTRACTOR_PROFILE_INVALID",
        label="profile steps key",
        value=key,
        problem=f"The steps key {key!r} can never match a file.",
        expected="'*' or a lowercase suffix such as '.py'",
        verbose=False,
    )


def test_a_single_action_needs_no_key_check(dummy_action) -> None:
    """Only a mapping has keys to check."""
    assert Profile("python", "x", steps=dummy_action).steps is dummy_action


@pytest.mark.parametrize("steps", ["not-an-action", 5, ["x"], {123: "x"}, {".py": "not-an-action"}])
def test_wrong_steps_type_is_rejected_by_the_type_layer(steps) -> None:
    with pytest.raises(ValidationError):
        Profile("python", "x", steps=steps)


# ---------------------------------------------------------------- the other fields

@pytest.mark.parametrize("format_name", ["Markdown", "two words", "", "-x", "1x", "a.b"])
def test_wrong_format_shape_is_rejected_by_the_type_layer(format_name) -> None:
    """The shape of a format name is part of the `OutputFormat` type, so validation rejects it."""
    with pytest.raises(ValidationError):
        Profile("python", "x", format=format_name)


@pytest.mark.parametrize("field", ["include", "exclude"])
@pytest.mark.parametrize("value", ["txt", 5, ["rule"]])
def test_include_and_exclude_must_be_rules(field, value) -> None:
    with pytest.raises(ValidationError):
        Profile("python", "x", **{field: value})


@pytest.mark.parametrize("description", [None, 5])
def test_description_must_be_text(description) -> None:
    with pytest.raises(ValidationError):
        Profile("python", "x", description=description)


# ---------------------------------------------------------------- frozen, slots, replace, equality

def test_profile_is_frozen() -> None:
    """A registered profile is shared by every run, so nobody may change it."""
    profile = Profile("python", "x")
    with pytest.raises(FrozenInstanceError):
        profile.name = "y"  # type: ignore[misc]


def test_profile_uses_slots() -> None:
    assert not hasattr(Profile("python", "x"), "__dict__")


def test_replace_makes_a_changed_copy() -> None:
    profile = Profile("python", "x", description="d")
    changed = replace(profile, name="y")
    assert changed.key == "python/y"
    assert changed.description == "d"
    assert profile.key == "python/x"


def test_replace_checks_the_new_value_again() -> None:
    """A copy with a bad name fails the same way as a new profile with a bad name."""
    with pytest.raises(ParamError):
        replace(Profile("python", "x"), name="a/b")


def test_profiles_with_the_same_values_are_equal() -> None:
    assert Profile("python", "x") == Profile("python", "x")
    assert Profile("python", "x") != Profile("python", "y")
