import pytest
from simplibs.exception import ParamError, ValidationError
from simplibs.exception.testing import assert_exception_function
from simplibs.extractor.logic.report import estimate_tokens


@pytest.mark.parametrize(
    "text, expected",
    [
        ("", 0),
        ("a", 1),          # a started token is a token
        ("abcd", 1),
        ("abcde", 2),
        ("abcdefgh", 2),
        ("abcdefghi", 3),
        ("a" * 1_000_000, 250_000),
    ],
)
def test_default_is_four_characters_per_token(text, expected) -> None:
    assert estimate_tokens(text) == expected


@pytest.mark.parametrize(
    "text, ratio, expected",
    [
        ("abcdef", 2.0, 3),
        ("abcdefg", 2.0, 4),
        ("abcdef", 1.0, 6),
        ("abcdef", 0.5, 12),
        ("abcdefghij", 3.0, 4),     # 3.33 rounds up
        ("abcdef", 100.0, 1),
        ("", 2.0, 0),
    ],
)
def test_own_ratio(text, ratio, expected) -> None:
    assert estimate_tokens(text, ratio) == expected


def test_ratio_can_be_given_by_keyword() -> None:
    assert estimate_tokens("abcdef", chars_per_token=2.0) == 3


def test_characters_are_counted_not_bytes() -> None:
    assert estimate_tokens("žžžž") == 1
    assert estimate_tokens("ž" * 5) == 2


def test_new_lines_and_spaces_count_like_any_character() -> None:
    assert estimate_tokens("a\n b") == 1
    assert estimate_tokens("a\r\n b") == 2


def test_the_result_is_an_int() -> None:
    assert type(estimate_tokens("abcde")) is int


def test_a_whole_number_ratio_is_accepted() -> None:
    assert estimate_tokens("abcdef", 2) == 3


@pytest.mark.parametrize("ratio", [0.0, -1.0, -0.5])
def test_a_ratio_that_is_not_positive_gives_a_config_invalid_card(subtests, ratio) -> None:
    assert_exception_function(
        subtests,
        estimate_tokens,
        invalid_params=("abc", ratio),
        valid_params=("abc",),
        exception_type=ParamError,
        error_name="EXTRACTOR_CONFIG_INVALID",
        label="parameter 'chars_per_token'",
        value=ratio,
        problem="The number of characters per token must be positive.",
        expected="A number greater than zero (about 4 for English text and code).",
        how_to_fix="Pass a positive number, or leave the default.",
        verbose=False,
    )


@pytest.mark.parametrize("text", [None, 5, b"abc", ["a"]])
def test_the_text_must_be_a_string(text) -> None:
    with pytest.raises(ValidationError):
        estimate_tokens(text)


@pytest.mark.parametrize("ratio", ["4", None, [4.0]])
def test_the_ratio_must_be_a_number(ratio) -> None:
    with pytest.raises(ValidationError):
        estimate_tokens("abc", ratio)
