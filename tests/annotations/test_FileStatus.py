from typing import get_args
import pytest
from simplibs.rules import IsTyping
from simplibs.extractor.annotations import FileStatus


@pytest.mark.parametrize("value", ["ok", "skipped", "error"])
def test_file_status_accepts_valid_outcomes(value) -> None:
    """Valid file statuses ('ok', 'skipped', 'error') are accepted."""
    assert IsTyping(FileStatus).is_valid(value)


@pytest.mark.parametrize("value", ["success", "failed", "OK", "", None, 1])
def test_file_status_rejects_everything_else(value) -> None:
    """Invalid statuses, wrong case, and non-strings are rejected."""
    assert not IsTyping(FileStatus).is_valid(value)


def test_file_status_has_exactly_the_three_outcomes() -> None:
    """The set of literal values is exactly ok / skipped / error (a removed or added value fails here)."""
    assert set(get_args(FileStatus)) == {"ok", "skipped", "error"}
    assert len(get_args(FileStatus)) == 3
