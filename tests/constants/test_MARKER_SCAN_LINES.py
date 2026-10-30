from simplibs.extractor.constants import MARKER_SCAN_LINES


def test_value() -> None:
    """The marker scan covers the first 3 lines of a file."""
    assert MARKER_SCAN_LINES == 3
    assert isinstance(MARKER_SCAN_LINES, int)