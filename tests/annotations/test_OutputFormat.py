from typing import Annotated, get_args, get_origin
import pytest
from simplibs.rules import IsTyping
from simplibs.validate.testing import assert_type_contract
from simplibs.extractor.annotations import OutputFormat
from simplibs.extractor.annotations._helpers import is_output_format


@pytest.mark.parametrize("value", ["markdown", "plain", "json-manifest", "custom-format"])
def test_output_format_accepts_valid_names(value) -> None:
    """A valid format name shape is accepted."""
    assert IsTyping(OutputFormat).is_valid(value)


@pytest.mark.parametrize("value", ["Markdown", "markdown format", "", None, 42, ["markdown"]])
def test_output_format_rejects_everything_else(value) -> None:
    """Invalid format names and non-string types are rejected."""
    assert not IsTyping(OutputFormat).is_valid(value)


def test_output_format_contract(subtests) -> None:
    """Verify OutputFormat satisfies both the Rule contract and @validate_call integration."""
    assert_type_contract(
        subtests,
        type_=OutputFormat,
        valid_values=["markdown", "plain", "json-manifest"],
        invalid_values=["Markdown", "markdown format", "", None, 42],
        verbose=False,
    )


def test_output_format_is_an_annotated_str() -> None:
    """Spelled as `Annotated`, so editors and type checkers see a plain `str` with a predicate attached."""
    assert get_origin(OutputFormat) is Annotated
    assert get_args(OutputFormat) == (str, is_output_format)