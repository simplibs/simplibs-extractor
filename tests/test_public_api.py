import importlib
from pathlib import Path
import pytest
import simplibs.extractor as extractor

EXPECTED = {
    # Running an extraction
    "extract", "extract_many", "extract_here", "generate_local_script",
    # Profiles and formats
    "expand_profile_keys", "get_profile", "get_renderer", "list_formats", "list_profiles",
    "list_systems", "register_profile", "register_renderer", "load_plugins",
    # Data objects
    "Entry", "ExtractionConfig", "ExtractionResult", "FileReport", "Profile", "RenderContext",
    # Reporting
    "estimate_tokens", "format_summary",
    # Annotations and constants
    "FileStatus", "OutputFormat", "OverwritePolicy", "StepsSpec", "DEFAULT_PROFILE_KEY", "GENERATED_MARKER",
}

SUBPACKAGES = {"annotations", "cli", "constants", "definitions", "logic", "plugins", "registry", "scripts"}


def test_the_public_names_are_exactly_the_agreed_ones() -> None:
    """Adding or removing a public name is a decision; it must change this test on purpose."""
    assert set(extractor.__all__) == EXPECTED
    assert len(extractor.__all__) == 27


def test_no_name_is_listed_twice() -> None:
    assert len(extractor.__all__) == len(set(extractor.__all__))


@pytest.mark.parametrize("name", sorted(EXPECTED))
def test_every_public_name_exists(name) -> None:
    assert hasattr(extractor, name)


def test_a_star_import_brings_exactly_the_public_names() -> None:
    namespace: dict = {}
    exec("from simplibs.extractor import *", namespace)
    namespace.pop("__builtins__")
    assert set(namespace) == EXPECTED


def test_nothing_else_is_public() -> None:
    """Besides the public names, the package shows only its own sub-packages."""
    public = {name for name in dir(extractor) if not name.startswith("_")}
    assert public - set(extractor.__all__) <= SUBPACKAGES


def test_run_cli_is_not_in_the_root_but_in_the_cli_package() -> None:
    assert "run_cli" not in extractor.__all__
    assert not hasattr(extractor, "run_cli")
    assert callable(importlib.import_module("simplibs.extractor.cli").run_cli)


def test_the_two_constants_have_their_documented_values() -> None:
    assert extractor.DEFAULT_PROFILE_KEY == "generic/all"
    assert extractor.GENERATED_MARKER == "simplibs-extractor:generated"


def test_the_functions_and_classes_are_what_they_say() -> None:
    for name in ["extract", "extract_many", "extract_here", "generate_local_script", "get_profile", "get_renderer",
                 "list_formats", "list_profiles", "list_systems", "register_profile", "register_renderer",
                 "load_plugins", "expand_profile_keys", "estimate_tokens", "format_summary"]:
        assert callable(getattr(extractor, name)), name
    for name in ["Entry", "ExtractionConfig", "ExtractionResult", "FileReport", "Profile", "RenderContext"]:
        assert isinstance(getattr(extractor, name), type), name


def test_the_package_is_marked_as_typed() -> None:
    assert (Path(extractor.__file__).parent / "py.typed").is_file()


def test_the_package_can_be_run_as_a_module() -> None:
    assert (Path(extractor.__file__).parent / "__main__.py").is_file()
