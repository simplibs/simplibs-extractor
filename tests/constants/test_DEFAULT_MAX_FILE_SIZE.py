from simplibs.extractor.constants import DEFAULT_MAX_FILE_SIZE


def test_value() -> None:
    """The default max file size is one megabyte (1,000,000 bytes)."""
    assert DEFAULT_MAX_FILE_SIZE == 1_000_000
    assert isinstance(DEFAULT_MAX_FILE_SIZE, int)