import pytest
from simplibs.actions import Action
from simplibs.style import styles_disabled


@pytest.fixture(autouse=True)
def plain_text():
    """Keep every printed line free of escape codes, whatever NO_COLOR / FORCE_COLOR say."""
    with styles_disabled():
        yield


@pytest.fixture(autouse=True)
def isolated_registries():
    """Give every test the registries as they were at import, and put them back afterwards.

    Both registries are module-level dictionaries, so whatever one test registers
    would otherwise stay visible to every later test.
    """
    from simplibs.extractor.registry._helpers import PROFILE_REGISTRY, RENDERER_REGISTRY

    profiles = dict(PROFILE_REGISTRY)
    renderers = dict(RENDERER_REGISTRY)
    try:
        yield
    finally:
        PROFILE_REGISTRY.clear()
        PROFILE_REGISTRY.update(profiles)
        RENDERER_REGISTRY.clear()
        RENDERER_REGISTRY.update(renderers)


@pytest.fixture
def dummy_action():
    """A minimal real Action (text in, text out) for tests that need some action instance."""

    class DummyAction(Action):
        def __call__(self, text: str) -> str:
            return text

        def run(self, text: str) -> str:
            return text

    return DummyAction()


@pytest.fixture
def make_action():
    """Build a real Action from a function: `make_action(str.upper)` or `make_action(lambda t: 5, name="Broken")`.

    Both `__call__` and `run` call the function, so it does not matter which one the framework uses.
    """

    def _make(func, name: str = "FuncAction") -> Action:
        class FuncAction(Action):
            def __call__(self, text):
                return func(text)

            def run(self, text):
                return func(text)

        FuncAction.__name__ = name
        FuncAction.__qualname__ = name
        return FuncAction()

    return _make
