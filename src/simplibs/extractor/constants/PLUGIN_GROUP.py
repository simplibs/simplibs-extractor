from typing import Final


PLUGIN_GROUP: Final[str] = "simplibs.extractor.plugins"
"""The entry-point group in which add-on packages announce themselves."""


_DESIGN_NOTES = """
# PLUGIN_GROUP — How an Add-On Is Found Without Being Imported

## Purpose
An add-on such as `simplibs-code-extractor` declares in its `pyproject.toml`:

    [project.entry-points."simplibs.extractor.plugins"]
    code = "simplibs.code_extractor:register_all"

The extractor looks the group up when the command line starts, so the
profiles of every installed add-on exist without the extractor knowing any of
them by name.
"""
