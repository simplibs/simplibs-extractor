from simplibs.extractor.constants import PLUGIN_GROUP


def test_value() -> None:
    """The entry-point group for add-ons is `simplibs.extractor.plugins`."""
    assert PLUGIN_GROUP == "simplibs.extractor.plugins"
    assert isinstance(PLUGIN_GROUP, str)