# Running an extraction
from .logic import extract, extract_many
from .scripts import extract_here, generate_local_script

# Profiles and formats
from .registry import (
    expand_profile_keys,
    get_profile,
    get_renderer,
    list_formats,
    list_profiles,
    list_systems,
    register_profile,
    register_renderer,
)
from .plugins import load_plugins

# Data objects
from .definitions import Entry, ExtractionConfig, ExtractionResult, FileReport, Profile
from .logic import RenderContext

# Reporting
from .logic import estimate_tokens, format_summary

# Annotations and constants
from .annotations import FileStatus, OutputFormat, OverwritePolicy, StepsSpec
from .constants import DEFAULT_PROFILE_KEY, GENERATED_MARKER


__all__ = [
    # Running an extraction
    "extract",
    "extract_many",
    "extract_here",
    "generate_local_script",
    # Profiles and formats
    "expand_profile_keys",
    "get_profile",
    "get_renderer",
    "list_formats",
    "list_profiles",
    "list_systems",
    "register_profile",
    "register_renderer",
    "load_plugins",
    # Data objects
    "Entry",
    "ExtractionConfig",
    "ExtractionResult",
    "FileReport",
    "Profile",
    "RenderContext",
    # Reporting
    "estimate_tokens",
    "format_summary",
    # Annotations and constants
    "FileStatus",
    "OutputFormat",
    "OverwritePolicy",
    "StepsSpec",
    "DEFAULT_PROFILE_KEY",
    "GENERATED_MARKER",
]


_DESIGN_NOTES = """
# simplibs.extractor — Universal File Extractor

Gathers the text files of a folder into one document: select, read,
transform, render, write, report. The core knows no language; add-ons bring
profiles (`simplibs-code-extractor` is the first).

## Layers (each one looks only to the left)

`annotations` <- `constants` <- `exceptions` <- `definitions` <- `registry`
<- `logic` <- `plugins` <- `scripts` <- `cli`

## The Public Surface

Everything a program needs is in this module. The command line is the one
exception: `from simplibs.extractor.cli import run_cli`. It is not imported
here, so a program that only calls `extract()` does not load the prompt and
logger libraries it would never use.

## Internal Components Registry

| Component                | Type      | Description                                                    |
| :----------------------- | :-------- | :------------------------------------------------------------- |
| `extract`                | Function  | One extraction through all six phases.                         |
| `extract_many`           | Function  | Several extractions; a failed one does not stop the rest.      |
| `extract_here`           | Function  | Extracts the folder of a script into a file next to it.        |
| `generate_local_script`  | Function  | Writes a ready-to-run local extraction script.                 |
| `register_profile`       | Function  | Adds a profile to the registry.                                |
| `get_profile`            | Function  | Returns a profile by its `system/name` key.                    |
| `list_profiles`          | Function  | Lists the registered profiles.                                 |
| `list_systems`           | Function  | Lists the systems that have a profile.                         |
| `expand_profile_keys`    | Function  | Turns typed names into full profile keys.                      |
| `register_renderer`      | Function  | Adds an output format.                                         |
| `get_renderer`           | Function  | Returns the renderer of a format.                              |
| `list_formats`           | Function  | Lists the registered output formats.                           |
| `load_plugins`           | Function  | Lets every installed add-on register its profiles.             |
| `Profile`                | Dataclass | A named set of selection rules and transformation steps.       |
| `ExtractionConfig`       | Dataclass | Everything one run needs to know.                              |
| `ExtractionResult`       | Dataclass | The outcome of one run; the source of every report.            |
| `FileReport`             | Dataclass | What happened to one file.                                     |
| `Entry`                  | Dataclass | One file ready to be rendered.                                 |
| `RenderContext`          | Dataclass | What a renderer knows besides the entries.                     |
| `format_summary`         | Function  | Readable text from an `ExtractionResult`.                      |
| `estimate_tokens`        | Function  | A rough token count of a text.                                 |
| `FileStatus`             | Type      | `ok`, `skipped` or `error`.                                    |
| `OutputFormat`           | Type      | The name of an output format.                                  |
| `OverwritePolicy`        | Type      | `overwrite`, `unique`, `backup` or `error`.                    |
| `StepsSpec`              | Type      | One action, a suffix -> action mapping, or nothing.            |
| `DEFAULT_PROFILE_KEY`    | Constant  | The built-in profile `generic/all`.                            |
| `GENERATED_MARKER`       | Constant  | The text that marks a file as an output of this library.       |

## Importing Has Two Side Effects
The built-in profile `generic/all` and the formats `markdown` and `plain` are
registered. Nothing else happens until a function is called; add-ons are only
looked up by `load_plugins()` (the command line calls it).
"""
