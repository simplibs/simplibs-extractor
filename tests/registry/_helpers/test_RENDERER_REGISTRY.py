from simplibs.extractor.registry._helpers import RENDERER_REGISTRY


def test_is_a_dict_of_callables_by_format_name() -> None:
    assert isinstance(RENDERER_REGISTRY, dict)
    for name, renderer in RENDERER_REGISTRY.items():
        assert isinstance(name, str)
        assert callable(renderer)


def test_built_in_formats_are_registered_after_import() -> None:
    """Importing the package registers `markdown` and `plain`."""
    assert {"markdown", "plain"} <= set(RENDERER_REGISTRY)
