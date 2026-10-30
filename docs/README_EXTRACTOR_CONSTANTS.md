# 🔢 `constants` — Fixed Values

The `constants` package holds the fixed values the library agrees on with itself: the default limits and
names, the marker that identifies an output, the table of code-fence languages, the entry-point group of the
add-ons and the text of a generated script. Two of them — the ones a program meets most often — are exported
from the package root; all of them live in `simplibs.extractor.constants`:

```python
from simplibs.extractor import DEFAULT_PROFILE_KEY, GENERATED_MARKER

from simplibs.extractor.constants import (
    DEFAULT_MAX_FILE_SIZE, DEFAULT_OUTPUT_NAME, DEFAULT_PROFILE_KEY, DEFAULT_SCRIPT_NAME,
    GENERATED_MARKER, LANGUAGE_BY_SUFFIX, MARKER_SCAN_LINES, PLUGIN_GROUP, SCRIPT_TEMPLATE,
)
```

Every one of them is a **defaults and agreements** value, not a setting: where a value can be changed, it
is changed through the field or parameter that *starts* from it (`ExtractionConfig.max_file_size`,
`Profile.output_name`, `load_plugins(group=...)`), never by assigning to the constant. They are declared
`Final`, and the one table (`LANGUAGE_BY_SUFFIX`) is read-only.

## Four groups

| Group                 | Constants                                                                  | What they agree on                                              |
|-----------------------|----------------------------------------------------------------------------|-----------------------------------------------------------------|
| **Defaults**          | `DEFAULT_MAX_FILE_SIZE`, `DEFAULT_OUTPUT_NAME`, `DEFAULT_PROFILE_KEY`      | what a run does when nothing else is said                       |
| **Recognizing output**| `GENERATED_MARKER`, `MARKER_SCAN_LINES`                                    | how the library knows a file is its own output                  |
| **Output**            | `LANGUAGE_BY_SUFFIX`                                                       | the language of a code fence in the Markdown output             |
| **Wiring**            | `PLUGIN_GROUP`, `DEFAULT_SCRIPT_NAME`, `SCRIPT_TEMPLATE`                   | how add-ons are found and how a local script is written         |

## Where each one is used

| Constant                | Used by                                                                                         |
|-------------------------|-------------------------------------------------------------------------------------------------|
| `DEFAULT_MAX_FILE_SIZE` | the default of `ExtractionConfig.max_file_size`                                                 |
| `DEFAULT_OUTPUT_NAME`   | the default of `Profile.output_name`                                                            |
| `DEFAULT_PROFILE_KEY`   | `resolve_profile` (no profile chosen), `failure_result`, the default of the prompt in `simplibs-extractor init` |
| `DEFAULT_SCRIPT_NAME`   | `generate_local_script` (a folder was given instead of a file name)                             |
| `GENERATED_MARKER`      | both built-in renderers (they write it), `is_generated_file` (it looks for it)                  |
| `MARKER_SCAN_LINES`     | `is_generated_file`                                                                             |
| `LANGUAGE_BY_SUFFIX`    | the `markdown` renderer                                                                         |
| `PLUGIN_GROUP`          | the default of `load_plugins(group=...)`                                                        |
| `SCRIPT_TEMPLATE`       | `render_script`, and through it `generate_local_script` and `simplibs-extractor init`           |

---

## 🧭 Table of Contents

**Defaults**

* [`DEFAULT_MAX_FILE_SIZE`](#default_max_file_size)
* [`DEFAULT_OUTPUT_NAME`](#default_output_name)
* [`DEFAULT_PROFILE_KEY`](#default_profile_key)

**Recognizing output**

* [`GENERATED_MARKER`](#generated_marker)
* [`MARKER_SCAN_LINES`](#marker_scan_lines)

**Output**

* [`LANGUAGE_BY_SUFFIX`](#language_by_suffix)

**Wiring**

* [`PLUGIN_GROUP`](#plugin_group)
* [`DEFAULT_SCRIPT_NAME`](#default_script_name)
* [`SCRIPT_TEMPLATE`](#script_template)

[⬅️ Back to main README](../README.md#-annotations-and-constants)

---

### `DEFAULT_MAX_FILE_SIZE`

The **largest file, in bytes, that is read into an extraction** — one megabyte.

**Definition:**

```python
DEFAULT_MAX_FILE_SIZE: Final[int] = 1_000_000
```

**Used as:** the default of `ExtractionConfig.max_file_size`. A larger file is not read; it is reported as
`skipped` with its size and the limit as the reason.

**Example usage:**

```python
from simplibs.extractor import ExtractionConfig, extract
from simplibs.extractor.constants import DEFAULT_MAX_FILE_SIZE

DEFAULT_MAX_FILE_SIZE                                           # -> 1000000

ExtractionConfig(source="my_project").max_file_size             # -> 1000000     the default
ExtractionConfig(source="my_project", max_file_size=200_000)    # a tighter limit for this run
ExtractionConfig(source="my_project", max_file_size=None)       # no limit at all

result = extract(source="my_project", dry_run=True)
[(f.relative, f.reason) for f in result.skipped_files]
# -> [('data/dump.json', 'too large (1500000 > 1000000 bytes)')]
```

**Why there is a limit.** A single lock file or data dump can be larger than the rest of the project
together and would drown the output. It is **reported, not dropped silently**: the file stays in the
result with its reason, so "why is my file missing?" always has an answer.

**Not a fixed rule.** The constant is only where the field starts; `max_file_size=` overrides it and `None`
switches the limit off.

<details>
<summary>🔍 Under the hood</summary>

```python
DEFAULT_MAX_FILE_SIZE: Final[int] = 1_000_000
"""The largest file, in bytes, that is read into an extraction."""
```

It is the default of one field, and the read phase reports the skip with the numbers in the reason:

```python
max_size: ByteCount | None = DEFAULT_MAX_FILE_SIZE      # ExtractionConfig

return FileReport(path, relative, "skipped", f"too large ({size} > {max_size} bytes)", size), None   # read_source
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `DEFAULT_OUTPUT_NAME`

The **file name of an output** when a profile does not choose its own.

**Definition:**

```python
DEFAULT_OUTPUT_NAME: Final[str] = "extraction.md"
```

**Used as:** the default of `Profile.output_name`. The target of a run is `source / profile.output_name`
unless `target` is set.

**Example usage:**

```python
from simplibs.extractor import Profile
from simplibs.extractor.constants import DEFAULT_OUTPUT_NAME

DEFAULT_OUTPUT_NAME                                             # -> 'extraction.md'

Profile(system="demo", name="all").output_name                  # -> 'extraction.md'
Profile(system="demo", name="clean", output_name="clean.md").output_name   # -> 'clean.md'
```

**Why the name comes from the profile.** On the command line `-o` is a **folder**; the file name always
comes from the profile. Several profiles in one run therefore produce several files instead of overwriting
one. A profile that does not choose a name starts from this one.

<details>
<summary>🔍 Under the hood</summary>

```python
DEFAULT_OUTPUT_NAME: Final[str] = "extraction.md"
"""The file name of an output when a profile does not choose its own."""
```

```python
output_name: str = DEFAULT_OUTPUT_NAME                  # Profile
```

```python
# 4. The profile, and from it the default target and format        (resolve_config)
target = normalize_path(config.target) if config.target is not None else source / profile.output_name
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `DEFAULT_PROFILE_KEY`

The **key of the built-in profile** that is used when none is chosen — `"generic/all"`.

**Definition:**

```python
DEFAULT_PROFILE_KEY: Final[str] = "generic/all"
```

**Used as:** the profile of a run whose `profile` is `None`, the profile named in a failed run that never got
as far as choosing one, and the preselected answer of the profile prompt in `simplibs-extractor init`.

**Example usage:**

```python
from simplibs.extractor import DEFAULT_PROFILE_KEY, extract, get_profile

DEFAULT_PROFILE_KEY                                             # -> 'generic/all'
get_profile(DEFAULT_PROFILE_KEY).description                    # the built-in profile: every text file, unchanged

extract(source="my_project")                                    # the same as ...
extract(source="my_project", profile=DEFAULT_PROFILE_KEY)       # ... this
```

**Why a built-in default.** `generic/all` takes every text file and changes nothing, so the extractor is
useful **without any language add-on installed**. The profile itself is registered when the package is
imported; see [the registry](README_EXTRACTOR_REGISTRY.md).

<details>
<summary>🔍 Under the hood</summary>

```python
DEFAULT_PROFILE_KEY: Final[str] = "generic/all"
"""The key of the built-in profile used when none is chosen."""
```

```python
# resolve_profile
if profile is None:
    return get_profile(DEFAULT_PROFILE_KEY)
```

```python
# failure_result
key = profile or DEFAULT_PROFILE_KEY
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `GENERATED_MARKER`

The **text every output carries in its first lines** to mark it as generated by this library.

**Definition:**

```python
GENERATED_MARKER: Final[str] = "simplibs-extractor:generated"
```

**Used as:** a plain substring. The built-in renderers write it in the form that suits their format; the
read phase looks for it as plain text.

| Format     | First line of the output                      |
|------------|-----------------------------------------------|
| `markdown` | `<!-- simplibs-extractor:generated -->`       |
| `plain`    | `# simplibs-extractor:generated`              |

**Example usage:**

```python
from simplibs.extractor import GENERATED_MARKER, register_renderer

def render_names(entries, context):                             # a renderer of your own
    names = "\n".join(entry.relative for entry in entries)
    return f"# {GENERATED_MARKER}\n{names}\n"                   # the marker keeps this output out of the next run

register_renderer("names", render_names)
```

**Why the path is not enough.** An extraction that lands inside its own source folder would be read again
by the next run. The `unique` policy makes `extraction (1).md` and `backup` makes a backup file — names
nobody could list in advance. The marker identifies an output **whatever it is called**, backups included.

**A custom format must write it.** A renderer of your own is responsible for putting the marker into the
first lines of its output (see the example). Without it the output is read as an ordinary file the next
time the folder is extracted.

<details>
<summary>🔍 Under the hood</summary>

```python
GENERATED_MARKER: Final[str] = "simplibs-extractor:generated"
"""The text every output carries in its first lines to mark it as generated."""
```

Written by hand, as plain text, by the renderers:

```python
# render_markdown
return f"<!-- {GENERATED_MARKER} -->\n\n{body}\n"

# render_plain
lines = [
    f"# {GENERATED_MARKER}",
    ...
]
```

Looked for by [`is_generated_file`](logic/README_EXTRACTOR_READ.md) in the first `MARKER_SCAN_LINES` lines:

```python
return any(GENERATED_MARKER in line for line in head)
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `MARKER_SCAN_LINES`

**How many leading lines of a file are searched** for `GENERATED_MARKER`.

**Definition:**

```python
MARKER_SCAN_LINES: Final[int] = 3
```

**Example usage:**

```python
from simplibs.extractor import GENERATED_MARKER
from simplibs.extractor.constants import MARKER_SCAN_LINES

MARKER_SCAN_LINES                                               # -> 3

# an output whose marker is in line 1, 2 or 3 is recognized;
# a file that merely mentions the marker on line 4 or later is an ordinary file
```

**Why only the head.** Outputs are large. Reading the first lines keeps the check cheap and makes it
independent of the size limit — a multi-megabyte output costs a few kilobytes.

**Why three and not one.** A format may put a title or a front-matter line before the marker; three
lines leave room for that without ever scanning content.

<details>
<summary>🔍 Under the hood</summary>

```python
MARKER_SCAN_LINES: Final[int] = 3
"""How many leading lines of a file are searched for `GENERATED_MARKER`."""
```

```python
# is_generated_file
lines = iter_lines(path, errors="replace")
with closing(lines):
    head = list(islice(lines, MARKER_SCAN_LINES))
```

The file is streamed and closed right after the head.

</details>

[▲ Back to top](#-table-of-contents)

---

### `LANGUAGE_BY_SUFFIX`

The **code-fence language** of a file suffix, for syntax highlighting in the Markdown output.

**Definition:**

```python
LANGUAGE_BY_SUFFIX: Final[MappingProxyType[str, str]] = MappingProxyType({...})
```

| Suffix           | Language       | Suffix    | Language    |
|------------------|----------------|-----------|-------------|
| `.py`            | `python`       | `.html`   | `html`      |
| `.js`            | `javascript`   | `.toml`   | `toml`      |
| `.jsx`           | `jsx`          | `.yml`    | `yaml`      |
| `.ts`            | `typescript`   | `.yaml`   | `yaml`      |
| `.tsx`           | `tsx`          | `.sh`     | `bash`      |
| `.json`          | `json`         | `.sql`    | `sql`       |
| `.md`            | `markdown`     | `.txt`    | `text`      |
| `.css`           | `css`          |           |             |

**Example usage:**

```python
from simplibs.extractor.constants import LANGUAGE_BY_SUFFIX

LANGUAGE_BY_SUFFIX[".py"]                                       # -> 'python'
LANGUAGE_BY_SUFFIX[".yml"]                                      # -> 'yaml'
LANGUAGE_BY_SUFFIX.get(".rs")                                   # -> None        not in the table

LANGUAGE_BY_SUFFIX[".py"] = "py3"                               # raises TypeError — the table is read-only
```

**What an unknown suffix gets.** The renderer first asks this table and, if the suffix is not in it,
uses the suffix itself without the dot — a `.rs` file is fenced as `rs`. A file **without** a suffix gets a
plain fence with no language.

**Why a suffix.** A fenced block in Markdown is highlighted by its language name, and the suffix is the
cheapest reliable way to choose it.

**Why read-only.** It is a `MappingProxyType`, so no caller can change the table for everyone else in the
same process.

<details>
<summary>🔍 Under the hood</summary>

```python
LANGUAGE_BY_SUFFIX: Final[MappingProxyType[str, str]] = MappingProxyType({
    ".py": "python",
    ".js": "javascript",
    ...
    ".txt": "text",
})
```

The only reader is the `markdown` renderer:

```python
# 1. An empty file has nothing to fence
code = entry.text.rstrip("\n")
if not code.strip():
    return Paragraph("(empty file)")

# 2. The language of the fence from the suffix; unknown suffixes get a plain fence
suffix = entry.suffix.lower()
language = LANGUAGE_BY_SUFFIX.get(suffix, suffix.lstrip("."))
return CodeBlock(code, language) if language else CodeBlock(code)
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `PLUGIN_GROUP`

The **entry-point group** in which add-on packages announce themselves.

**Definition:**

```python
PLUGIN_GROUP: Final[str] = "simplibs.extractor.plugins"
```

**Used as:** the default of `load_plugins(group=...)`.

**Example usage:**

An add-on declares itself in its own `pyproject.toml`:

```toml
[project.entry-points."simplibs.extractor.plugins"]
code = "simplibs.code_extractor:register_all"
```

and the extractor finds it **without importing it by name**:

```python
from simplibs.extractor import load_plugins
from simplibs.extractor.constants import PLUGIN_GROUP

PLUGIN_GROUP                                                    # -> 'simplibs.extractor.plugins'

loaded, failed = load_plugins()                                 # every installed add-on registers its profiles
```

**Why an entry-point group.** The profiles of every installed add-on exist without the extractor knowing
any of them by name. Installing a package is enough.

Writing an add-on is described in [the plugins reference](README_EXTRACTOR_PLUGINS.md).

<details>
<summary>🔍 Under the hood</summary>

```python
PLUGIN_GROUP: Final[str] = "simplibs.extractor.plugins"
"""The entry-point group in which add-on packages announce themselves."""
```

```python
def load_plugins(
    *,
    group: str = PLUGIN_GROUP,
    ...
```

The extractor looks the group up when the command line starts, before the parser is built.

</details>

[▲ Back to top](#-table-of-contents)

---

### `DEFAULT_SCRIPT_NAME`

The **file name of a generated local script** when only a folder is given.

**Definition:**

```python
DEFAULT_SCRIPT_NAME: Final[str] = "extract_here.py"
```

**Example usage:**

```python
from simplibs.extractor import generate_local_script
from simplibs.extractor.constants import DEFAULT_SCRIPT_NAME

DEFAULT_SCRIPT_NAME                                             # -> 'extract_here.py'

generate_local_script("my_project")                             # writes my_project/extract_here.py
generate_local_script("my_project/run_extraction.py")           # an explicit name wins
```

The same happens on the command line: `simplibs-extractor init my_project`.

**Why this name.** It says what the script does, and it is the name a person finds again months later.

<details>
<summary>🔍 Under the hood</summary>

```python
DEFAULT_SCRIPT_NAME: Final[str] = "extract_here.py"
"""The file name of a generated local script when only a folder is given."""
```

```python
# generate_local_script
target = target / DEFAULT_SCRIPT_NAME
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `SCRIPT_TEMPLATE`

The **text of a generated local script**. `{file_name}` and `{profile}` are filled in.

**Definition:**

```python
SCRIPT_TEMPLATE: Final[str] = '''#!/usr/bin/env python3
"""Local extraction of this folder. Generated by simplibs-extractor.

Run it with:  python {file_name}
"""
from simplibs.extractor import extract_here

if __name__ == "__main__":
    extract_here(__file__, profile={profile!r})
'''
```

**Example usage:**

```python
from simplibs.extractor.constants import SCRIPT_TEMPLATE

print(SCRIPT_TEMPLATE.format(file_name="extract_here.py", profile="python/code-clean"))
```

```python
#!/usr/bin/env python3
"""Local extraction of this folder. Generated by simplibs-extractor.

Run it with:  python extract_here.py
"""
from simplibs.extractor import extract_here

if __name__ == "__main__":
    extract_here(__file__, profile='python/code-clean')
```

You normally do not format it yourself — [`generate_local_script`](README_EXTRACTOR_SCRIPTS.md) does.

**Why so little logic.** The script holds **no path and no configuration**: `extract_here(__file__, ...)`
takes the folder from where the script lies, so it can be dropped into any project.

**Why a `__main__` guard.** Importing the script (a test, an editor's indexer) must not start an
extraction.

**Why `{profile!r}`.** The profile key is written as a Python literal, quotes included, so no key can
break the generated code.

<details>
<summary>🔍 Under the hood</summary>

```python
def render_script(file_name: str, profile_key: str) -> str:
    # 1. `{profile!r}` writes the key as a Python literal, so no key can break the code
    return SCRIPT_TEMPLATE.format(file_name=file_name, profile=profile_key)
```

`render_script` is split from `generate_local_script` so the text of the script can be tested — compiled,
even run — without touching the disk.

</details>

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../README.md#-annotations-and-constants)
