from pathlib import Path
import pytest
from simplibs.extractor.logic.select._validations import raise_source_not_found_error
from simplibs.extractor.logic.write._validations import raise_target_exists_error
from simplibs.extractor.logic._common import describe_failure


@pytest.mark.parametrize(
    "exc, expected",
    [
        (ValueError("boom"), "ValueError: boom"),
        (OSError("disk gone"), "OSError: disk gone"),
        (KeyError("x"), "KeyError: 'x'"),
        (RuntimeError("line one\nline two"), "RuntimeError: line one"),
        (RuntimeError("\n\n  padded  \nsecond"), "RuntimeError: padded"),
        (RuntimeError("42"), "RuntimeError: 42"),
        (RuntimeError("příliš žluťoučký"), "RuntimeError: příliš žluťoučký"),
    ],
    ids=["ValueError", "OSError", "KeyError", "two-lines", "blank-first-lines", "digits-only", "non-ascii"],
)
def test_describe_failure_is_the_class_name_and_the_first_line_with_content(exc, expected) -> None:
    """One readable line, whatever the message looks like."""
    assert describe_failure(exc) == expected


@pytest.mark.parametrize("message", ["", "   ", "\n\n", "════════", "─────\n═════", "\n═══\n   \n"])
def test_describe_failure_a_message_without_content_gives_only_the_class_name(message) -> None:
    """Blank lines and frames made of box characters carry no information."""
    assert describe_failure(RuntimeError(message)) == "RuntimeError"


def test_describe_failure_skips_the_frame_of_a_card() -> None:
    """A card prints as a framed block of several lines; only the first line with real content is kept."""
    try:
        raise_source_not_found_error(Path("missing"))
    except Exception as card:
        description = describe_failure(card)

    assert description.startswith("NotFoundError: ")
    assert "\n" not in description
    assert "═" not in description and "─" not in description


def test_describe_failure_names_the_class_of_every_card() -> None:
    """The class is always first, so a report shows what kind of failure it was."""
    try:
        raise_target_exists_error(Path("out.md"))
    except Exception as card:
        assert describe_failure(card).startswith("AlreadyExistsError")
