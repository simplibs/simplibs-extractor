from simplibs.rules import IsTyping, Rule
from simplibs.rules.testing import assert_rule_contract
from simplibs.extractor.logic.select import any_of


def test_no_rule_gives_none() -> None:
    assert any_of() is None


def test_only_nones_give_none() -> None:
    assert any_of(None) is None
    assert any_of(None, None, None) is None


def test_one_rule_is_returned_as_it_is() -> None:
    """Nothing to combine, nothing is wrapped."""
    rule = IsTyping(int)
    assert any_of(rule) is rule
    assert any_of(None, rule, None) is rule


def test_two_rules_need_one_to_pass() -> None:
    combined = any_of(IsTyping(int), IsTyping(str))
    assert isinstance(combined, Rule)
    assert combined(1) is True
    assert combined("a") is True
    assert combined(1.5) is False


def test_none_between_rules_is_ignored() -> None:
    combined = any_of(IsTyping(int), None, IsTyping(str))
    assert combined(1) is True
    assert combined("a") is True
    assert combined(None) is False


def test_three_rules_need_one_of_three() -> None:
    combined = any_of(IsTyping(int), IsTyping(str), IsTyping(float))
    assert combined(1.5) is True
    assert combined(b"x") is False


def test_combined_rule_is_a_well_formed_rule(subtests) -> None:
    """The result keeps the whole Rule contract (booleans, validate modes, diagnostic card)."""
    assert_rule_contract(
        subtests,
        any_of(IsTyping(int), IsTyping(str)),
        valid_values=[1, "a"],
        invalid_values=[1.5, None, b"x"],
        verbose=False,
    )
