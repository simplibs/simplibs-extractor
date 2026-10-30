# Phase 1: Which files
from .select import resolve_config, select_sources

# Phase 2: What is in the files
from .read import is_generated_file, read_source

# Phase 3: Clean the text
from .transform import apply_steps, steps_for

# Phase 4: Turn entries into text
from .render import RenderContext, build_tree, render_markdown, render_plain

# Phase 5: Put it on the disk
from .write import write_output

# Phase 6: Say what happened
from .report import estimate_tokens, format_summary

# The run that joins the phases
from .extract import extract
from .extract_many import extract_many
from .failure_result import failure_result


__all__ = [
    # Phase 1
    "resolve_config",
    "select_sources",
    # Phase 2
    "is_generated_file",
    "read_source",
    # Phase 3
    "apply_steps",
    "steps_for",
    # Phase 4
    "RenderContext",
    "build_tree",
    "render_markdown",
    "render_plain",
    # Phase 5
    "write_output",
    # Phase 6
    "estimate_tokens",
    "format_summary",
    # The run
    "extract",
    "extract_many",
    "failure_result",
]


_DESIGN_NOTES = """
# logic — The Functional Core

Plain imports, with an `__all__`: this is the declared surface of the core.
Six phase packages, and above them the run that joins them.

## Two Levels of Public

`simplibs.extractor` re-exports what most programs need. What is in the
`__all__` here is the second level: for a program that builds its own
pipeline out of the phases. Both are supported; the root is the shorter one.

## Layout

The phases (`select`, `read`, `transform`, `render`, `write`, `report`) do
not import each other. `_common` holds what several of them need, `_helpers`
what only the run needs.

## Internal Components Registry

| Component           | Type      | Description                                         |
| :------------------ | :-------- | :-------------------------------------------------- |
| `RenderContext`     | Dataclass | Phase 4: the context of a renderer.                 |
| `apply_steps`       | Function  | Phase 3: runs the steps of a profile on a text.     |
| `build_tree`        | Function  | Phase 4: draws a directory tree.                    |
| `estimate_tokens`   | Function  | Phase 6: a rough token count.                       |
| `extract`           | Function  | The whole extraction.                               |
| `extract_many`      | Function  | Several extractions in a row.                       |
| `failure_result`    | Function  | A result for a run that could not start.            |
| `format_summary`    | Function  | Phase 6: readable text from a result.               |
| `is_generated_file` | Function  | Phase 2: recognizes the library's own outputs.      |
| `read_source`       | Function  | Phase 2: reads one file or says why not.            |
| `render_markdown`   | Function  | Phase 4: the Markdown format.                       |
| `render_plain`      | Function  | Phase 4: the plain format.                          |
| `resolve_config`    | Function  | Phase 1: fills in defaults, checks the config.      |
| `select_sources`    | Function  | Phase 1: collects the files an extraction takes.    |
| `steps_for`         | Function  | Phase 3: picks the action for a suffix.             |
| `write_output`      | Function  | Phase 5: writes the output by the overwrite policy. |
"""