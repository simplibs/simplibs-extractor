from dataclasses import FrozenInstanceError
from pathlib import Path
import pytest
from simplibs.extractor.definitions import ExtractionConfig, Profile, Resolved


def _resolved() -> Resolved:
    config = ExtractionConfig(source=Path("project"))
    return Resolved(config, Profile("python", "code"), "markdown")


def test_resolved_keeps_its_three_values() -> None:
    """Resolved holds the config, the profile object and the format that will be used."""
    resolved = _resolved()
    assert isinstance(resolved.config, ExtractionConfig)
    assert isinstance(resolved.profile, Profile)
    assert resolved.format == "markdown"


def test_resolved_is_frozen() -> None:
    """Later phases cannot change what was resolved."""
    with pytest.raises(FrozenInstanceError):
        _resolved().format = "plain"  # type: ignore[misc]


def test_resolved_uses_slots() -> None:
    """No per-instance __dict__."""
    assert not hasattr(_resolved(), "__dict__")
