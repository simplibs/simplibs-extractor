from collections.abc import Sequence
# Outers
from ...constants import GENERATED_MARKER
from ...definitions import Entry
# Inners
from .RenderContext import RenderContext
from .build_tree import build_tree


def render_plain(
    entries: Sequence[Entry],
    context: RenderContext,
) -> str:
    """Render the entries as plain text in the layout of the old code extractor.

    Args:
        entries: The files, in output order.
        context: Title, source, profile and tree switch.

    Returns:
        The whole output: a header, an optional tree and `# FILE: path` blocks.
    """

    # 1. Header: the marker comes first, so the read phase finds it
    lines = [
        f"# {GENERATED_MARKER}",
        f"# {context.title}",
        f"# profile: {context.profile_key}",
        "",
    ]

    # 2. Optional tree
    if context.add_tree and entries:
        lines += ["# TREE", build_tree([entry.relative for entry in entries]), ""]

    # 3. One block per file
    for entry in entries:
        lines += [f"# FILE: {entry.relative}", entry.text.rstrip("\n"), ""]

    # 4. Exactly one line ending at the end
    return "\n".join(lines).rstrip("\n") + "\n"


_DESIGN_NOTES = """
# render_plain — The Old Layout, for Tools That Expect It

## Purpose
`# FILE: path` blocks as the old extractor wrote them, for pipelines that
split on that line.

## The Marker Is the First Line
Within `MARKER_SCAN_LINES`, in every format; this is what keeps the output
out of the next run.

## No Absolute Path
The source folder is not written (see `RenderContext`).
"""
