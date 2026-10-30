from collections.abc import Sequence
from simplibs.markdown import CodeBlock, Document, InlineCode, MarkdownText, Paragraph
from simplibs.markdown.presets import H1, H2
# Outers
from ...constants import GENERATED_MARKER, LANGUAGE_BY_SUFFIX
from ...definitions import Entry
# Inners
from .RenderContext import RenderContext
from .build_tree import build_tree


def render_markdown(
    entries: Sequence[Entry],
    context: RenderContext,
) -> str:
    """Render the entries as a Markdown document.

    Args:
        entries: The files, in output order.
        context: Title, source, profile and tree switch.

    Returns:
        The whole output: a marker comment, a title, an optional tree, and a
        heading with a fenced code block for each file.
    """

    # 1. Title and a line about where the content came from
    blocks = [
        H1(context.title),
        Paragraph("Profile: " + InlineCode(context.profile_key)),
    ]

    # 2. Optional tree
    if context.add_tree and entries:
        blocks.append(CodeBlock(build_tree([entry.relative for entry in entries]), "text"))

    # 3. One heading and one code block per file
    for entry in entries:
        blocks.append(H2(InlineCode(entry.relative)))
        blocks.append(_code_of(entry))

    # 4. The marker is written as plain text: its presence is what the read phase relies on
    body = MarkdownText(Document(*blocks)).text.rstrip("\n")
    return f"<!-- {GENERATED_MARKER} -->\n\n{body}\n"


def _code_of(entry: Entry):
    """The block that shows one file: a fenced block, or a note for an empty file."""

    # 1. An empty file has nothing to fence
    code = entry.text.rstrip("\n")
    if not code.strip():
        return Paragraph("(empty file)")

    # 2. The language of the fence from the suffix; unknown suffixes get a plain fence
    suffix = entry.suffix.lower()
    language = LANGUAGE_BY_SUFFIX.get(suffix, suffix.lstrip("."))
    return CodeBlock(code, language) if language else CodeBlock(code)


_DESIGN_NOTES = """
# render_markdown — The Default Output

## Purpose
A document that reads well in a viewer and pastes well into a chat: a title,
the tree, then every file under its path in a fenced block.

## The Fence Fits the Code
`CodeBlock` chooses a fence longer than any run of backticks inside the code,
so a Markdown file with its own code blocks cannot break the output.

## Paths Are Inline Code
`my_file.py` as a plain heading would be escaped (`my\\_file.py`). Inline
code shows it exactly as it is.

## The Marker Is Plain Text
The comment is written by hand rather than built as a node: if it ever
failed to appear, outputs would be read back as input. `_code_of` is local
because only this renderer needs it.

## To Do
Replace the hand-written comment with the `COMMENT` preset once its README
confirms it can be the first element of a `Document`.
"""
