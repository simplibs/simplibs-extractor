from simplibs.extractor.logic.render import register_builtin_renderers, render_markdown, render_plain
from simplibs.extractor.registry import get_renderer, list_formats, register_renderer
from simplibs.extractor.registry._helpers import RENDERER_REGISTRY


def _other(entries, context) -> str:
    return "other"


def test_the_two_built_in_formats_are_registered_with_their_renderers() -> None:
    RENDERER_REGISTRY.clear()
    register_builtin_renderers()
    assert get_renderer("markdown") is render_markdown
    assert get_renderer("plain") is render_plain
    assert list_formats() == ["markdown", "plain"]


def test_calling_it_again_does_not_fail() -> None:
    """Importing the package twice (or reloading it) must not break on the library's own formats."""
    register_builtin_renderers()
    register_builtin_renderers()
    assert get_renderer("markdown") is render_markdown


def test_it_restores_a_built_in_format_that_was_replaced() -> None:
    register_renderer("markdown", _other, replace_existing=True)
    register_builtin_renderers()
    assert get_renderer("markdown") is render_markdown


def test_it_leaves_other_formats_alone() -> None:
    register_renderer("custom", _other)
    register_builtin_renderers()
    assert get_renderer("custom") is _other


def test_it_returns_nothing() -> None:
    assert register_builtin_renderers() is None
