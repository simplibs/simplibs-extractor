from simplibs.extractor.constants import DEFAULT_PROFILE_KEY


def test_value() -> None:
    """The default built-in profile key is `generic/all`."""
    assert DEFAULT_PROFILE_KEY == "generic/all"
    assert isinstance(DEFAULT_PROFILE_KEY, str)