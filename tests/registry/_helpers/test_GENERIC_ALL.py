from dataclasses import FrozenInstanceError
import pytest
from simplibs.extractor.constants import DEFAULT_OUTPUT_NAME, DEFAULT_PROFILE_KEY
from simplibs.extractor.definitions import Profile
from simplibs.extractor.registry._helpers import GENERIC_ALL


def test_is_a_profile_with_the_default_key() -> None:
    """The built-in profile lives under the key the rest of the library uses as its default."""
    assert isinstance(GENERIC_ALL, Profile)
    assert GENERIC_ALL.key == DEFAULT_PROFILE_KEY
    assert (GENERIC_ALL.system, GENERIC_ALL.name) == ("generic", "all")


def test_selects_everything_and_changes_nothing() -> None:
    """No rules, no steps: every text file, unchanged."""
    assert GENERIC_ALL.include is None
    assert GENERIC_ALL.exclude is None
    assert GENERIC_ALL.steps is None


def test_uses_the_default_output() -> None:
    assert GENERIC_ALL.output_name == DEFAULT_OUTPUT_NAME
    assert GENERIC_ALL.format == "markdown"


def test_has_a_description_for_the_listing() -> None:
    assert GENERIC_ALL.description.strip()


def test_is_frozen() -> None:
    """It is shared by every run."""
    with pytest.raises(FrozenInstanceError):
        GENERIC_ALL.name = "other"  # type: ignore[misc]
