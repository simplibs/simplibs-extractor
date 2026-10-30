from simplibs.rules import IsTyping, Rule
from simplibs.rules.testing import assert_rule_contract
from simplibs.extractor.logic.select import all_of


def test_no_rule_gives_none() -> None:
    assert all_of() is None


def test_only_nones_give_none() -> None:
    assert all_of(None) is None
    assert all_of(None, None, None) is None


def test_one_rule_is_returned_as_it_is() -> None:
    """Nothing to combine, nothing is wrapped."""
    rule = IsTyping(int)
    assert all_of(rule) is rule
    assert all_of(None, rule, None) is rule


def test_two_rules_need_both_to_pass() -> None:
    combined = all_of(IsTyping(int), IsTyping(bool))
    assert isinstance(combined, Rule)
    assert combined(True) is True        # a bool is an int and a bool
    assert combined(1) is False          # an int, but not a bool
    assert combined("x") is False


def test_none_between_rules_is_ignored() -> None:
    combined = all_of(IsTyping(int), None, IsTyping(bool))
    assert combined(True) is True
    assert combined(1) is False


def test_three_rules_need_all_three() -> None:
    combined = all_of(IsTyping(int), IsTyping(bool), IsTyping(object))
    assert combined(True) is True
    assert combined(1) is False


def test_combined_rule_is_a_well_formed_rule(subtests) -> None:
    """The result keeps the whole Rule contract (booleans, validate modes, diagnostic card)."""
    assert_rule_contract(
        subtests,
        all_of(IsTyping(int), IsTyping(bool)),
        valid_values=[True, False],
        invalid_values=[1, "x", None],
        verbose=False,
    )
