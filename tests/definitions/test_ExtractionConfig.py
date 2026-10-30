from dataclasses import FrozenInstanceError, replace
from pathlib import Path
import pytest
from simplibs.exception import ValidationError
from simplibs.rules import IsTyping
from simplibs.extractor.constants import DEFAULT_MAX_FILE_SIZE
from simplibs.extractor.definitions import ExtractionConfig, Profile


# ---------------------------------------------------------------- defaults and raw values

def test_defaults() -> None:
    """Only `source` is required; everything else has its documented default."""
    config = ExtractionConfig(source=Path("project"))
    assert config.target is None
    assert config.profile is None
    assert config.include is None
    assert config.exclude is None
    assert config.ignore_names is None
    assert config.recursive is True
    assert config.format is None
    assert config.overwrite == "overwrite"
    assert config.dry_run is False
    assert config.max_file_size == DEFAULT_MAX_FILE_SIZE
    assert config.add_tree is True
    assert config.title is None
    assert config.skip_paths == ()


def test_values_are_stored_as_given() -> None:
    """Nothing is normalized here - `resolve_config` does that later."""
    config = ExtractionConfig(source="src", target="out/x.md", profile="python/code-clean")
    assert config.source == "src"
    assert config.target == "out/x.md"
    assert config.profile == "python/code-clean"


# ---------------------------------------------------------------- accepted values

@pytest.mark.parametrize("source", ["src", Path("src"), "../up", "~/project"])
def test_accepts_source_as_text_or_path(source) -> None:
    assert ExtractionConfig(source=source).source == source


@pytest.mark.parametrize("target", [None, "out.md", Path("out/out.md")])
def test_accepts_target(target) -> None:
    assert ExtractionConfig(source="src", target=target).target == target


def test_accepts_profile_as_key_object_or_none() -> None:
    profile = Profile("python", "code")
    assert ExtractionConfig(source="src", profile="python/code").profile == "python/code"
    assert ExtractionConfig(source="src", profile=profile).profile is profile
    assert ExtractionConfig(source="src", profile=None).profile is None


def test_accepts_rules_for_include_and_exclude() -> None:
    rule = IsTyping(str)
    config = ExtractionConfig(source="src", include=rule, exclude=rule)
    assert config.include is rule
    assert config.exclude is rule


@pytest.mark.parametrize("names", [frozenset({"node_modules"}), frozenset()])
def test_accepts_ignore_names_as_frozenset(names) -> None:
    """An empty frozenset is a real choice ('ignore nothing'), different from None ('use the default')."""
    assert ExtractionConfig(source="src", ignore_names=names).ignore_names == names


@pytest.mark.parametrize("policy", ["overwrite", "unique", "backup", "error"])
def test_accepts_every_overwrite_policy(policy) -> None:
    assert ExtractionConfig(source="src", overwrite=policy).overwrite == policy


@pytest.mark.parametrize("value", [None, 1, 5_000_000])
def test_accepts_max_file_size(value) -> None:
    """None switches the limit off."""
    assert ExtractionConfig(source="src", max_file_size=value).max_file_size == value


def test_accepts_skip_paths_as_tuple_of_paths_and_texts() -> None:
    config = ExtractionConfig(source="src", skip_paths=("a.py", Path("b.py")))
    assert config.skip_paths == ("a.py", Path("b.py"))


def test_accepts_format_title_and_flags() -> None:
    config = ExtractionConfig(
        source="src", format="plain", title="My code", recursive=False, dry_run=True, add_tree=False
    )
    assert (config.format, config.title) == ("plain", "My code")
    assert (config.recursive, config.dry_run, config.add_tree) == (False, True, False)


# ---------------------------------------------------------------- rejected values

@pytest.mark.parametrize(
    "kwargs",
    [
        {"source": None},
        {"source": 5},
        {"source": ""},
        {"source": "   "},
        {"source": "src", "target": 5},
        {"source": "src", "target": ""},
        {"source": "src", "profile": 5},
        {"source": "src", "include": "txt"},
        {"source": "src", "include": 5},
        {"source": "src", "exclude": "txt"},
        {"source": "src", "ignore_names": ["node_modules"]},
        {"source": "src", "ignore_names": frozenset({1})},
        {"source": "src", "recursive": "yes"},
        {"source": "src", "format": "Markdown"},
        {"source": "src", "format": "two words"},
        {"source": "src", "overwrite": "force"},
        {"source": "src", "dry_run": "no"},
        {"source": "src", "max_file_size": -1},
        {"source": "src", "max_file_size": "big"},
        {"source": "src", "add_tree": 1},
        {"source": "src", "title": 5},
        {"source": "src", "skip_paths": ("",)},
        {"source": "src", "skip_paths": (5,)},
    ],
)
def test_rejects_invalid_values(kwargs) -> None:
    """A config is user input: a wrong type or shape fails when it is built, not during the run."""
    with pytest.raises(ValidationError):
        ExtractionConfig(**kwargs)


def test_source_is_required() -> None:
    with pytest.raises(TypeError):
        ExtractionConfig()  # type: ignore[call-arg]


# ---------------------------------------------------------------- frozen, slots, replace

def test_config_is_frozen() -> None:
    config = ExtractionConfig(source="src")
    with pytest.raises(FrozenInstanceError):
        config.dry_run = True  # type: ignore[misc]


def test_config_uses_slots() -> None:
    assert not hasattr(ExtractionConfig(source="src"), "__dict__")


def test_replace_makes_a_changed_copy() -> None:
    """`extract(**overrides)` relies on this: one change, the rest stays."""
    config = ExtractionConfig(source="src", title="T")
    changed = replace(config, dry_run=True)
    assert changed.dry_run is True
    assert changed.title == "T"
    assert config.dry_run is False


def test_replace_validates_the_new_value() -> None:
    """A bad override is rejected just like a bad constructor argument."""
    with pytest.raises(ValidationError):
        replace(ExtractionConfig(source="src"), overwrite="force")


def test_configs_with_the_same_values_are_equal() -> None:
    assert ExtractionConfig(source="src") == ExtractionConfig(source="src")
    assert ExtractionConfig(source="src") != ExtractionConfig(source="other")
