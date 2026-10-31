import importlib.metadata
from types import SimpleNamespace

import pytest
from simplibs.exception import NotFoundError
from simplibs.extractor import Profile, extract_here, generate_local_script, register_profile
from simplibs.extractor.constants import PLUGIN_GROUP
from simplibs.extractor.registry._helpers import PROFILE_REGISTRY

KEY = "fake/demo"


def _register_demo() -> None:
    """The registration function of the pretend add-on."""
    register_profile(
        Profile(system="fake", name="demo", output_name="fake_demo.md"),
        replace_existing=True,
    )


@pytest.fixture
def fake_addon(monkeypatch):
    """One pretend installed add-on that registers `fake/demo`; the registry is cleaned afterwards."""
    entry_point = SimpleNamespace(name="fake", load=lambda: _register_demo)
    monkeypatch.setattr(
        importlib.metadata,
        "entry_points",
        lambda *, group: [entry_point] if group == PLUGIN_GROUP else [],
    )
    PROFILE_REGISTRY.pop(KEY, None)
    yield
    PROFILE_REGISTRY.pop(KEY, None)


@pytest.fixture
def no_addons(monkeypatch):
    """No add-on installed."""
    monkeypatch.setattr(importlib.metadata, "entry_points", lambda *, group: [])
    PROFILE_REGISTRY.pop(KEY, None)


@pytest.fixture
def forbidden_lookup(monkeypatch):
    """Looking for add-ons at all is a failure of the test."""
    def fail(*, group):
        raise AssertionError("add-ons must not be looked up for this profile")
    monkeypatch.setattr(importlib.metadata, "entry_points", fail)


@pytest.fixture
def project(tmp_path):
    """A folder with one text file and the script that lies in it."""
    (tmp_path / "notes.txt").write_text("hello\n", encoding="utf-8")
    script = tmp_path / "extract_here.py"
    script.write_text("# the script\n", encoding="utf-8")
    return tmp_path, script


# ----------------------------------------------------------------------------- extract_here

def test_extract_here_loads_the_addon_of_a_key(fake_addon, project) -> None:
    """A key of an add-on that is installed but not yet registered works."""

    folder, script = project

    result = extract_here(script, profile=KEY, quiet=True)

    assert result.success
    assert result.profile_key == KEY
    assert (folder / "fake_demo.md").is_file()


def test_extract_here_twice_is_safe(fake_addon, project) -> None:
    """The add-ons are loaded on every call; registering again must change nothing."""

    folder, script = project

    first = extract_here(script, profile=KEY, quiet=True)
    second = extract_here(script, profile=KEY, quiet=True)

    assert first.success and second.success


def test_extract_here_unknown_key_still_fails_clearly(no_addons, project) -> None:
    """With no add-on installed the card is still the one that lists the registered keys."""

    _, script = project

    with pytest.raises(NotFoundError):
        extract_here(script, profile=KEY, quiet=True)


def test_extract_here_profile_object_does_not_look_for_addons(forbidden_lookup, project) -> None:
    """A `Profile` needs nothing found."""

    folder, script = project
    profile = Profile(system="fake", name="direct", output_name="direct.md")

    result = extract_here(script, profile=profile, quiet=True)

    assert result.success
    assert (folder / "direct.md").is_file()


def test_extract_here_default_profile_does_not_look_for_addons(forbidden_lookup, project) -> None:
    """`None` means the built-in `generic/all`, which is always registered."""

    folder, script = project

    result = extract_here(script, quiet=True)

    assert result.success
    assert result.profile_key == "generic/all"


# ----------------------------------------------------------------------------- generate_local_script

def test_generate_local_script_loads_the_addon_of_a_key(fake_addon, tmp_path) -> None:
    """A script for a profile of an installed add-on can be written."""

    written = generate_local_script(tmp_path, profile=KEY)

    assert written == tmp_path / "extract_here.py"
    assert repr(KEY) in written.read_text(encoding="utf-8")


def test_generate_local_script_unknown_key_writes_nothing(no_addons, tmp_path) -> None:
    """A key nobody provides fails before anything is written."""

    with pytest.raises(NotFoundError):
        generate_local_script(tmp_path, profile=KEY)

    assert not (tmp_path / "extract_here.py").exists()


def test_generate_local_script_profile_object_does_not_look_for_addons(forbidden_lookup, tmp_path) -> None:
    """A `Profile` needs nothing found."""

    profile = Profile(system="fake", name="direct")

    written = generate_local_script(tmp_path, profile=profile)

    assert "fake/direct" in written.read_text(encoding="utf-8")