# 🖨️ `logic/render` — Phase 4: Turn Entries Into Text

The fourth phase takes **all the files that made it** — a list of [`Entry`](../README_EXTRACTOR_DEFINITIONS.md#entry)
objects — and turns them into **one text**: the output document. It is the only place where the layout of
the output is decided, and it is the only phase that is *chosen by name*: the format.

```
[Entry, Entry, ...] + RenderContext ──► renderer of the format ──► one str
   the files, in order                    "markdown" · "plain" · yours
```

The phase **never touches the disk**. A renderer receives entries and a context and returns a string; writing
that string is the [next phase](README_EXTRACTOR_WRITE.md). That is what makes a renderer easy to test with a
handful of hand-made entries.

```python
from pathlib import Path
from simplibs.extractor import Entry, RenderContext
from simplibs.extractor.logic import render_plain

entries = [
    Entry("README.md", ".md", "# My project\n\nA small demo.\n"),
    Entry("src/app.py", ".py", "import os\n"),
]
context = RenderContext(title="Extraction: my_project", source=Path("my_project"),
                        profile_key="generic/all", add_tree=True)

print(render_plain(entries, context))
```

```text
# simplibs-extractor:generated
# Extraction: my_project
# profile: generic/all

# TREE
├── src/
│   └── app.py
└── README.md

# FILE: README.md
# My project

A small demo.

# FILE: src/app.py
import os
```

In `extract()` the phase runs once, after every file has been read and transformed: the renderer of the
resolved format is taken from the [registry](../README_EXTRACTOR_REGISTRY.md#get_renderer) and called with the
entries of all files whose status is `ok`. If **no file made it**, the renderer is not called at all — nothing
is rendered and nothing is written.

## The two built-in formats

| Format     | Renderer          | What the output looks like                                                                                   |
|------------|-------------------|--------------------------------------------------------------------------------------------------------------|
| `markdown` | `render_markdown` | A marker comment, a title, `Profile: ...`, an optional tree, then a heading and a fenced block per file. **The default.** |
| `plain`    | `render_plain`    | The layout of the old code extractor: a header, an optional `# TREE` and `# FILE: path` blocks.              |

Both are registered when the render phase is imported — through the same
[`register_renderer`](../README_EXTRACTOR_REGISTRY.md#register_renderer) call a format of your own would use.

## Writing a renderer of your own

A renderer is a plain function:

```python
def renderer(entries: Sequence[Entry], context: RenderContext) -> str: ...
```

and it is **registered by name**. The contract:

| Rule                                                                                       | Why                                                                                   |
|--------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------|
| It receives the entries **in output order**, already filtered and transformed.             | The text of every entry is final — its steps have run and its line endings are `"\n"`.|
| It returns **one `str`** — the whole output.                                               | The write phase writes exactly that.                                                  |
| It writes `GENERATED_MARKER` **within the first three lines**, in whatever syntax the format allows. | Otherwise the output is read as an ordinary file the next time the folder is extracted. |
| It does not touch the disk and does not print.                                             | Rendering is a pure function; the run decides what is written and shown.              |
| It writes **no absolute path**.                                                            | An output is pasted into chats and committed; a path would leak the layout of the machine. |

A complete example — a JSON manifest. JSON has no comments, so the marker is the value of the second line:

```python
import json
from simplibs.extractor import GENERATED_MARKER, extract, register_renderer

def render_manifest(entries, context):
    manifest = {
        "generator": GENERATED_MARKER,                  # line 2: inside the first three lines
        "title": context.title,
        "files": [{"path": entry.relative, "chars": len(entry.text)} for entry in entries],
    }
    return json.dumps(manifest, indent=2) + "\n"

register_renderer("json-manifest", render_manifest)

extract(source="my_project", format="json-manifest", target="my_project/manifest.json")
```

```python
render_manifest(entries, context).splitlines()[:3]
# -> ['{', '  "generator": "simplibs-extractor:generated",', '  "title": "Extraction: my_project",']
```

## What is public

`RenderContext`, together with `Entry`, is exported from the package root — it is part of the renderer
contract. The functions of the phase are importable from `simplibs.extractor.logic`
(`render_markdown`, `render_plain`, `build_tree`; all in its `__all__`); `register_builtin_renderers` lives in
`simplibs.extractor.logic.render`.

---

## 🧭 Table of Contents

**What a renderer receives**

* [`RenderContext`](#rendercontext)

**The built-in renderers**

* [`render_markdown`](#render_markdown)
* [`render_plain`](#render_plain)

**Helpers**

* [`build_tree`](#build_tree)
* [`register_builtin_renderers`](#register_builtin_renderers)

[⬅️ Back to main README](../../README.md#-the-six-phases)

---

### `RenderContext`

**What a renderer needs to know besides the entries** — the heading, the source, the profile and the tree
switch.

**Attributes:**

| Name          | Type   | Description                                                                          |
|---------------|--------|--------------------------------------------------------------------------------------|
| `title`       | `str`  | The heading of the output.                                                           |
| `source`      | `Path` | The source folder.                                                                   |
| `profile_key` | `str`  | The key of the profile that produced the entries (`"python/code-clean"`).            |
| `add_tree`    | `bool` | Whether the output starts with a directory tree.                                     |

**Returns:** a frozen `RenderContext`. `extract()` builds one for you; you build one yourself when you test a
renderer.

**Example usage:**

```python
from pathlib import Path
from simplibs.extractor import RenderContext

context = RenderContext(
    title="Extraction: my_project",
    source=Path("my_project"),
    profile_key="generic/all",
    add_tree=True,
)

context.title                                           # -> 'Extraction: my_project'
context.add_tree = False                                # raises FrozenInstanceError
```

In a run, the title is the one of the config, or `Extraction: <name of the source folder>` — a filesystem
root has no name, so its whole path is used.

**Why one object and not several parameters.** A renderer is a function `(entries, context)`. The entries
are the content; the context is everything around it. Passing one object keeps the signature stable when a
field is added — renderers written today keep working.

**The source is a path, but its folder is not written out.** The built-in renderers never write
`context.source`; the default title carries only the **name** of the folder. An output is typically pasted into
a chat or committed, and an absolute path would leak the layout of the machine and make the output differ
between computers.

<details>
<summary>🔍 Under the hood</summary>

```python
@dataclass(frozen=True, slots=True)
class RenderContext:
    title: str
    source: Path
    profile_key: str
    add_tree: bool
```

Built once per run, right before rendering:

```python
# extract
if entries:
    context = RenderContext(build_title(cfg), cfg.source, profile.key, cfg.add_tree)
    rendered = get_renderer(plan.format)(entries, context)
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `render_markdown`

**Renders the entries as a Markdown document** — the default output. It reads well in a viewer and pastes well
into a chat.

**Parameters:**

| Name      | Type              | Description                          |
|-----------|-------------------|--------------------------------------|
| `entries` | `Sequence[Entry]` | The files, in output order.          |
| `context` | `RenderContext`   | Title, source, profile and tree switch. |

**Returns:** the whole output as a `str`: a marker comment, a title, an optional tree, and a heading with a
fenced code block for each file. It ends with exactly one line ending.

**Example usage:**

```python
from pathlib import Path
from simplibs.extractor import Entry, RenderContext
from simplibs.extractor.logic import render_markdown

entries = [
    Entry("README.md", ".md", "# My project\n\nA small demo.\n"),
    Entry("src/app.py", ".py", "import os\n"),
]
context = RenderContext("Extraction: my_project", Path("my_project"), "generic/all", add_tree=True)

print(render_markdown(entries, context))
```

````markdown
<!-- simplibs-extractor:generated -->

# Extraction: my_project

Profile: `generic/all`

```text
├── src/
│   └── app.py
└── README.md
```

## `README.md`

```markdown
# My project

A small demo.
```

## `src/app.py`

```python
import os
```
````

**The layout.**

| Part                | What is written                                                                              |
|---------------------|----------------------------------------------------------------------------------------------|
| the marker          | `<!-- simplibs-extractor:generated -->` — the very first line, written by hand               |
| the title           | a level-1 heading                                                                            |
| the profile         | `Profile: ` and the key as inline code                                                       |
| the tree            | a `text` block — only if `add_tree` is on and there is at least one entry                    |
| every file          | a level-2 heading with the **path as inline code**, then the text in a fenced block          |

**What happens with the text of a file.**

```python
# the fence always fits the code — a Markdown file with its own code blocks cannot break the output
Entry("NOTES.md", ".md", "```python\nx = 1\n```\n")     # fenced with four backticks

# the language comes from the suffix; an unknown suffix is used as it is, no suffix gives a plain fence
Entry("lib.rs", ".rs", "fn main() {}\n")                # fenced as ```rs
Entry("Makefile", "", "all:\n\ttrue\n")                 # fenced without a language

# an empty file (or one with only blank lines) is noted instead of fenced
Entry("__init__.py", ".py", "")                         # shown as: (empty file)
```

Trailing blank lines of a file are dropped, so every block ends right after the last line of code.

**Why the paths are inline code.** `my_file.py` as a plain heading would be escaped (`my\_file.py`); inline
code shows it exactly as it is.

**Why the fence fits the code.** `CodeBlock` of `simplibs-markdown` chooses a fence longer than any run of
backticks inside the code. An extractor meets Markdown files that contain code blocks all the time.

**Why the marker is written by hand.** It is plain text rather than a node: if it ever failed to appear,
outputs would be read back as input. The marker is what the [read phase](README_EXTRACTOR_READ.md#is_generated_file)
looks for.

<details>
<summary>🔍 Under the hood</summary>

```python
def render_markdown(
    entries: Sequence[Entry],
    context: RenderContext,
) -> str:

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
```

`_code_of` is local, because only this renderer needs it:

```python
def _code_of(entry: Entry):

    # 1. An empty file has nothing to fence
    code = entry.text.rstrip("\n")
    if not code.strip():
        return Paragraph("(empty file)")

    # 2. The language of the fence from the suffix; unknown suffixes get a plain fence
    suffix = entry.suffix.lower()
    language = LANGUAGE_BY_SUFFIX.get(suffix, suffix.lstrip("."))
    return CodeBlock(code, language) if language else CodeBlock(code)
```

The table of languages is [`LANGUAGE_BY_SUFFIX`](../README_EXTRACTOR_CONSTANTS.md#language_by_suffix).

</details>

[▲ Back to top](#-table-of-contents)

---

### `render_plain`

**Renders the entries as plain text in the layout of the old code extractor** — for pipelines that split on
the `# FILE:` line.

**Parameters:**

| Name      | Type              | Description                          |
|-----------|-------------------|--------------------------------------|
| `entries` | `Sequence[Entry]` | The files, in output order.          |
| `context` | `RenderContext`   | Title, source, profile and tree switch. |

**Returns:** the whole output as a `str`: a header, an optional tree and a `# FILE: path` block per file. It
ends with exactly one line ending.

**Example usage:**

```python
from simplibs.extractor.logic import render_plain

print(render_plain(entries, context))                   # `entries` and `context` as in render_markdown
```

```text
# simplibs-extractor:generated
# Extraction: my_project
# profile: generic/all

# TREE
├── src/
│   └── app.py
└── README.md

# FILE: README.md
# My project

A small demo.

# FILE: src/app.py
import os
```

```python
import dataclasses

render_plain(entries, dataclasses.replace(context, add_tree=False))     # the same, without the "# TREE" block
```

**The layout.**

| Part        | What is written                                                          |
|-------------|--------------------------------------------------------------------------|
| line 1      | `# simplibs-extractor:generated` — the marker                            |
| line 2      | `# <title>`                                                              |
| line 3      | `# profile: <key>`                                                       |
| the tree    | `# TREE`, the tree and a blank line — only if `add_tree` is on and there is at least one entry |
| every file  | `# FILE: <path>`, the text without trailing blank lines, a blank line    |

**The marker is the first line.** It lies within `MARKER_SCAN_LINES` in every format; that is what keeps the
output out of the next run.

**Why it exists.** Tools that already split the output of the old extractor on `# FILE:` keep working. The
format has no fences, so it is also the smallest one.

<details>
<summary>🔍 Under the hood</summary>

```python
def render_plain(
    entries: Sequence[Entry],
    context: RenderContext,
) -> str:

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
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `build_tree`

**Draws a directory tree from relative paths** — a reader (or a model) sees the shape of the project before
the first file.

**Parameters:**

| Name    | Type            | Description                                                      |
|---------|-----------------|------------------------------------------------------------------|
| `paths` | `Sequence[str]` | Relative paths with `/` separators (`"src/a.py"`).               |

**Returns:** the tree as a `str`, one line per name; an empty string for no paths.

**Example usage:**

```python
from simplibs.extractor.logic import build_tree

print(build_tree(["src/app.py", "src/config.py", "tests/test_app.py", "README.md"]))
```

```text
├── src/
│   ├── app.py
│   └── config.py
├── tests/
│   └── test_app.py
└── README.md
```

```python
build_tree([])                                          # -> ''
build_tree(["a.py"])                                    # -> '└── a.py'
```

**Folders first.** In every folder the subfolders come before the files — the order a file manager shows —
and each group is sorted alphabetically without regard to case. A folder gets a trailing `/`.

**Built from the selected files only.** Not from the disk: the tree shows exactly what is **in the output**,
never a folder whose files were all skipped.

**Library paths are always `/`.** The relative paths of `FileReport` and `Entry` use `/` on every machine,
so the tree is the same on Windows and elsewhere.

<details>
<summary>🔍 Under the hood</summary>

```python
def build_tree(paths: Sequence[str]) -> str:

    # 1. Fold the paths into nested dictionaries: {"src": {"a.py": {}}}
    root: dict = {}
    for path in paths:
        node = root
        for part in path.split("/"):
            node = node.setdefault(part, {})

    # 2. Draw it
    return "\n".join(format_tree_lines(root))
```

The drawing half is a private helper, so that building the nested structure and drawing it are two small,
separately testable steps:

```python
def format_tree_lines(node: dict, prefix: str = "") -> list[str]:

    # 1. Folders first, then files; alphabetical inside each group
    items = sorted(node.items(), key=lambda item: (0 if item[1] else 1, item[0].lower()))

    # 2. Draw every item, descending into folders
    lines: list[str] = []
    for index, (name, children) in enumerate(items):
        is_last = index == len(items) - 1
        lines.append(prefix + ("└── " if is_last else "├── ") + name + ("/" if children else ""))
        if children:
            lines.extend(format_tree_lines(children, prefix + ("    " if is_last else "│   ")))

    return lines
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `register_builtin_renderers`

**Registers the two built-in formats**, `markdown` and `plain`.

**Parameters:** none.

**Returns:** `None`.

**Example usage:**

```python
from simplibs.extractor import list_formats

list_formats()                                          # -> ['markdown', 'plain']      registered on import — nothing to call
```

You do not call it yourself: the render phase calls it when it is imported, which is before any
configuration can be resolved.

**Why the core uses the same door as everyone.** The built-in formats are registered like any later one, so
the core never branches on a format name. It registers with `replace_existing=True`, so importing the package
again — or reloading it — never fails on its own formats.

<details>
<summary>🔍 Under the hood</summary>

```python
def register_builtin_renderers() -> None:

    # 1. `replace_existing`: importing again (or reloading) must not fail on our own formats
    register_renderer("markdown", render_markdown, replace_existing=True)
    register_renderer("plain", render_plain, replace_existing=True)
```

```python
# logic/render/__init__.py — the one side effect of importing the render phase
register_builtin_renderers()
```

</details>

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../../README.md#-the-six-phases)
