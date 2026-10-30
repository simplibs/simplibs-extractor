from dataclasses import FrozenInstanceError, replace
import pytest
from simplibs.extractor.definitions import Entry


def test_entry_keeps_its_three_values() -> None:
    """Entry carries the relative path, the suffix and the final text - in this order."""
    entry = Entry("src/a.py", ".py", "print(1)\n")
    assert (entry.relative, entry.suffix, entry.text) == ("src/a.py", ".py", "print(1)\n")


def test_entry_is_frozen() -> None:
    """A renderer cannot change what it receives."""
    entry = Entry("a.txt", ".txt", "x")
    with pytest.raises(FrozenInstanceError):
        entry.text = "y"  # type: ignore[misc]


def test_entry_uses_slots() -> None:
    """No per-instance __dict__."""
    assert not hasattr(Entry("a.txt", ".txt", "x"), "__dict__")


def test_entries_with_the_same_values_are_equal() -> None:
    """Equality is by value; `replace` makes a changed copy."""
    entry = Entry("a.txt", ".txt", "x")
    assert entry == Entry("a.txt", ".txt", "x")
    assert entry != replace(entry, text="y")
