from simplibs.extractor.constants import GENERATED_MARKER


def test_value() -> None:
    """The marker identifying a generated file is `simplibs-extractor:generated`."""
    assert GENERATED_MARKER == "simplibs-extractor:generated"
    assert isinstance(GENERATED_MARKER, str)