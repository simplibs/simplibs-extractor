from simplibs.extractor.registry import list_formats, register_renderer
from simplibs.extractor.registry._helpers import RENDERER_REGISTRY


def fake_renderer(entries, context) -> str:
    return "rendered"


def test_lists_the_built_in_formats() -> None:
    assert {"markdown", "plain"} <= set(list_formats())


def test_sorted_alphabetically() -> None:
    RENDERER_REGISTRY.clear()
    for name in ["zeta", "alpha", "mid"]:
        register_renderer(name, fake_renderer)
    assert list_formats() == ["alpha", "mid", "zeta"]


def test_a_newly_registered_format_appears() -> None:
    register_renderer("custom", fake_renderer)
    assert "custom" in list_formats()


def test_empty_registry_has_no_formats() -> None:
    RENDERER_REGISTRY.clear()
    assert list_formats() == []


def test_returns_a_new_list_every_time() -> None:
    formats = list_formats()
    formats.append("invented")
    assert "invented" not in list_formats()
