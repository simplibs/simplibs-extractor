from typing import get_args
import pytest
from simplibs.rules import IsTyping
from simplibs.extractor.annotations import OverwritePolicy


@pytest.mark.parametrize("value", ["overwrite", "unique", "backup", "error"])
def test_overwrite_policy_accepts_valid_policies(value) -> None:
    """Valid policies ('overwrite', 'unique', 'backup', 'error') are accepted."""
    assert IsTyping(OverwritePolicy).is_valid(value)


@pytest.mark.parametrize("value", ["force", "skip", "OVERWRITE", "", None, 1])
def test_overwrite_policy_rejects_everything_else(value) -> None:
    """Invalid policies, wrong case, and non-strings are rejected."""
    assert not IsTyping(OverwritePolicy).is_valid(value)


def test_overwrite_policy_has_exactly_the_four_policies() -> None:
    """The set of literal values is exactly overwrite / unique / backup / error."""
    assert set(get_args(OverwritePolicy)) == {"overwrite", "unique", "backup", "error"}
    assert len(get_args(OverwritePolicy)) == 4
