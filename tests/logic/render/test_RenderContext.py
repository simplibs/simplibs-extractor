from dataclasses import FrozenInstanceError
from pathlib import Path
import pytest
from simplibs.extractor.logic.render import RenderContext


def test_render_context_keeps_its_four_values_in_order() -> None:
    """Title, source, profile key and tree switch - in this order (renderers of add-ons build it too)."""
    context = RenderContext("My code", Path("project"), "generic/all", True)
    assert context.title == "My code"
    assert context.source == Path("project")
    assert context.profile_key == "generic/all"
    assert context.add_tree is True


def test_render_context_is_frozen() -> None:
    context = RenderContext("T", Path("p"), "a/b", False)
    with pytest.raises(FrozenInstanceError):
        context.title = "other"  # type: ignore[misc]


def test_render_context_uses_slots() -> None:
    assert not hasattr(RenderContext("T", Path("p"), "a/b", False), "__dict__")


def test_all_four_values_are_required() -> None:
    with pytest.raises(TypeError):
        RenderContext("T", Path("p"), "a/b")  # type: ignore[call-arg]
