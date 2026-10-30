import importlib.metadata
import sys
import types
import pytest
from simplibs.extractor.constants import PLUGIN_GROUP
from simplibs.extractor.definitions import Profile
from simplibs.extractor.plugins import load_plugins
from simplibs.extractor.registry import get_profile, get_renderer, register_profile, register_renderer


class FakeEntryPoint:
    """The two things the loader uses of an entry point: `name` and `load()`."""

    def __init__(self, name: str, target) -> None:
        self.name = name
        self._target = target

    def load(self):
        if isinstance(self._target, BaseException):
            raise self._target
        return self._target


def _finder(*entry_points, seen: list | None = None):
    """A replacement for `importlib.metadata.entry_points` that returns the given entry points."""

    def finder(*, group):
        if seen is not None:
            seen.append(group)
        return list(entry_points)

    return finder


def _register_profile_plugin():
    register_profile(Profile("addon", "one"))


# ---------------------------------------------------------------- the result

def test_no_add_ons_give_empty_results() -> None:
    assert load_plugins(entry_points=_finder()) == ([], {})


def test_a_working_add_on_is_loaded_and_registers_its_profile() -> None:
    loaded, failed = load_plugins(entry_points=_finder(FakeEntryPoint("addon", _register_profile_plugin)))
    assert loaded == ["addon"]
    assert failed == {}
    assert get_profile("addon/one").key == "addon/one"


def test_an_add_on_may_register_a_renderer() -> None:
    def plugin():
        register_renderer("fancy", lambda entries, context: "fancy")

    load_plugins(entry_points=_finder(FakeEntryPoint("fancy", plugin)))
    assert callable(get_renderer("fancy"))


def test_the_names_are_listed_in_the_order_of_the_entry_points() -> None:
    entry_points = [FakeEntryPoint(name, lambda: None) for name in ["zeta", "alpha", "mid"]]
    loaded, _ = load_plugins(entry_points=_finder(*entry_points))
    assert loaded == ["zeta", "alpha", "mid"]


def test_the_return_value_of_the_add_on_is_ignored() -> None:
    loaded, failed = load_plugins(entry_points=_finder(FakeEntryPoint("addon", lambda: 42)))
    assert (loaded, failed) == (["addon"], {})


def test_the_result_is_a_pair_of_a_list_and_a_dict() -> None:
    loaded, failed = load_plugins(entry_points=_finder())
    assert isinstance(loaded, list)
    assert isinstance(failed, dict)


# ---------------------------------------------------------------- the group

def test_the_default_group_is_asked_for() -> None:
    seen: list[str] = []
    load_plugins(entry_points=_finder(seen=seen))
    assert seen == [PLUGIN_GROUP]


def test_another_group_can_be_asked_for() -> None:
    seen: list[str] = []
    load_plugins(group="my.group", entry_points=_finder(seen=seen))
    assert seen == ["my.group"]


def test_the_real_lookup_is_used_without_a_replacement(monkeypatch) -> None:
    seen: list[str] = []
    monkeypatch.setattr(importlib.metadata, "entry_points", _finder(seen=seen))
    assert load_plugins() == ([], {})
    assert seen == [PLUGIN_GROUP]


def test_the_real_lookup_finds_nothing_that_is_not_installed() -> None:
    loaded, failed = load_plugins(group="simplibs.extractor.plugins.that-nobody-uses")
    assert (loaded, failed) == ([], {})


def test_the_parameters_are_keyword_only() -> None:
    with pytest.raises(TypeError):
        load_plugins(PLUGIN_GROUP)  # type: ignore[misc]


# ---------------------------------------------------------------- a broken add-on

def test_an_add_on_that_cannot_be_imported_is_reported_with_one_line() -> None:
    entry_points = [FakeEntryPoint("bad", ImportError("No module named 'missing_thing'"))]
    loaded, failed = load_plugins(entry_points=_finder(*entry_points))
    assert loaded == []
    assert failed == {"bad": "ImportError: No module named 'missing_thing'"}


def test_an_add_on_that_raises_while_registering_is_reported() -> None:
    def plugin():
        raise RuntimeError("boom")

    loaded, failed = load_plugins(entry_points=_finder(FakeEntryPoint("bad", plugin)))
    assert loaded == []
    assert failed == {"bad": "RuntimeError: boom"}


def test_an_add_on_that_is_not_callable_is_reported() -> None:
    loaded, failed = load_plugins(entry_points=_finder(FakeEntryPoint("bad", "not a function")))
    assert loaded == []
    assert failed["bad"].startswith("TypeError")


def test_a_card_of_the_add_on_is_reported_as_one_line() -> None:
    """An add-on that registers a taken key gets the card of the registry - shortened to a line."""

    def plugin():
        register_profile(Profile("generic", "all"))

    _, failed = load_plugins(entry_points=_finder(FakeEntryPoint("greedy", plugin)))
    assert failed["greedy"].startswith("AlreadyExistsError")
    assert "\n" not in failed["greedy"]


def test_a_broken_add_on_does_not_stop_the_others() -> None:
    def bad():
        raise RuntimeError("boom")

    entry_points = [
        FakeEntryPoint("first", _register_profile_plugin),
        FakeEntryPoint("bad", bad),
        FakeEntryPoint("last", lambda: register_profile(Profile("addon", "two"))),
    ]
    loaded, failed = load_plugins(entry_points=_finder(*entry_points))

    assert loaded == ["first", "last"]
    assert list(failed) == ["bad"]
    assert get_profile("addon/one") and get_profile("addon/two")


def test_what_an_add_on_registered_before_it_failed_stays() -> None:
    def half():
        register_profile(Profile("addon", "half"))
        raise RuntimeError("boom")

    load_plugins(entry_points=_finder(FakeEntryPoint("half", half)))
    assert get_profile("addon/half").key == "addon/half"


def test_an_interrupt_is_not_swallowed() -> None:
    def plugin():
        raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        load_plugins(entry_points=_finder(FakeEntryPoint("stop", plugin)))


# ---------------------------------------------------------------- a real entry point object

def test_a_real_entry_point_object_is_loaded(monkeypatch) -> None:
    """`importlib.metadata.EntryPoint` imports the module and takes the named function out of it."""
    module = types.ModuleType("extractor_test_fake_addon")
    module.register = _register_profile_plugin
    monkeypatch.setitem(sys.modules, "extractor_test_fake_addon", module)
    real = importlib.metadata.EntryPoint(name="fake", value="extractor_test_fake_addon:register", group=PLUGIN_GROUP)

    loaded, failed = load_plugins(entry_points=_finder(real))

    assert (loaded, failed) == (["fake"], {})
    assert get_profile("addon/one").key == "addon/one"


def test_a_real_entry_point_to_a_missing_module_is_reported() -> None:
    real = importlib.metadata.EntryPoint(name="gone", value="extractor_test_no_such_module:register", group=PLUGIN_GROUP)

    loaded, failed = load_plugins(entry_points=_finder(real))

    assert loaded == []
    assert failed["gone"].startswith("ModuleNotFoundError")
