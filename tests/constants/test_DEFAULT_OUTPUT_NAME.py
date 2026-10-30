from simplibs.path import is_valid_filename
from simplibs.extractor.constants import DEFAULT_OUTPUT_NAME


def test_value() -> None:
    """The fallback file name of an output is `extraction.md`."""
    assert DEFAULT_OUTPUT_NAME == "extraction.md"
    assert isinstance(DEFAULT_OUTPUT_NAME, str)


def test_is_a_usable_file_name() -> None:
    """The default passes the same check a Profile applies to its `output_name`."""
    assert is_valid_filename(DEFAULT_OUTPUT_NAME)
