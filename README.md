# 🗂️ `simplibs-extractor`

[![PyPI](https://img.shields.io/pypi/v/simplibs-extractor)](https://pypi.org/project/simplibs-extractor/)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![Licence](https://img.shields.io/badge/licence-MIT-green)](https://github.com/simplibs/simplibs-extractor/blob/main/LICENSE)
[![tests](https://github.com/simplibs/simplibs-extractor/actions/workflows/tests.yml/badge.svg)](https://github.com/simplibs/simplibs-extractor/actions)

**Many files in, one document out — and a clear report of what happened to every one of them.**

A Python library, a command and a two-line script that gather the **text files of a folder into one
document**: pick the files, read them, clean their text with steps, render a Markdown (or plain)
document, write it atomically and tell you what was taken, what was left out and why. The core knows
**no language**: what a project looks like — which files, how to clean them — comes from **profiles**,
which add-on packages bring (`simplibs-code-extractor` is the first). On its own the extractor takes
every text file and changes nothing.

```bash
simplibs-extractor generic/all my_project
```

```
Extraction: generic/all
  source : /home/me/my_project
  target : /home/me/my_project/extraction.md (written)
  files  : 4 ok, 1 skipped, 0 errors
  size   : 133 B in -> 502 B out (~115 tokens)
  skipped: logo.png (not a text file)
```

```python
from simplibs.extractor import extract

result = extract(source="my_project")                 # the same extraction from Python
print(result.success, result.target)                  # -> True /home/me/my_project/extraction.md
```

> The extractor writes a **report, not a stream of prints**: every run returns an `ExtractionResult`
> that the command, a script or your own code turns into text, an exit code or a log. The only
> places that print are the command line and `extract_here` (for people running a script).

---

## 🧭 The Core Philosophy

Collecting a project into one file is easy to do badly: the output is read again on the next run, a
binary or a 50 MB lock file drowns everything, one unreadable file stops the whole job, a dry run
says "fine" and the real run fails. `simplibs-extractor` is built around those traps:

* **Six phases, each one a function.** `Select → Read → Transform → Render → Write → Report`. The
  run only wires them together, so each can be understood — and tested — alone.
* **The core knows no language.** Language knowledge lives in **profiles** (rules on paths + steps on
  text) registered by add-ons. A new kind of project is a new profile, not a change in the core.
* **One bad file never stops a run.** A file that cannot be read or transformed is a line in the
  report with its reason; the run continues. A configuration that cannot run fails **before any file
  is touched**.
* **`skipped` is not `error`.** A binary file, a file over the size limit, an earlier output — left
  out on purpose, not a problem. An `error` file was meant to be included and could not be; it makes
  the run unsuccessful.
* **The output is never its own input.** The target and the files you list are removed from the scan,
  and every output carries a **marker** in its first lines, so even `extraction (1).md` or a backup
  is recognised and skipped on the next run.
* **A dry run tells the truth.** It makes exactly the decisions a real run makes — including refusing
  an existing output under the `error` policy — and writes nothing.
* **Rules judge the relative path.** A project that merely lies inside a folder called `tests` is not
  dropped as "a test". What a rule can see is the path **inside** the source, so a profile works the
  same wherever the project is.
* **A config can only narrow.** The `include` you pass is combined with the profile's by AND, the
  `exclude` by OR; a config never widens what a profile selected.
* **Safe by default.** One megabyte per file, housekeeping folders (`.git`, `node_modules`, virtual
  environments, ...) and half-written drafts are never scanned, the output is written atomically
  (draft and swap), and only the **name** of the source folder — never its absolute path — goes into
  the output.
* **Every error is a card.** A wrong call is a structured card from
  [`simplibs-exception`](https://pypi.org/project/simplibs-exception/) with a name starting with
  `EXTRACTOR_`: what, why, how to fix. The library defines no exception classes of its own.
* **Layers that only look left.** `annotations` ← `constants` ← `definitions` ←
  `registry` ← `logic` ← `plugins` ← `scripts` ← `cli`.

---

## 📦 Installation

```bash
pip install simplibs-extractor
```

Requires Python 3.11+. The command is available as `simplibs-extractor` and as
`python -m simplibs.extractor`. Runtime dependencies, all from the same family:
[`simplibs-path`](https://pypi.org/project/simplibs-path/) and
[`simplibs-file`](https://pypi.org/project/simplibs-file/) (scanning, reading, atomic writing),
[`simplibs-rules`](https://pypi.org/project/simplibs-rules/) and
[`simplibs-actions`](https://pypi.org/project/simplibs-actions/) (the rules and steps of a profile),
[`simplibs-markdown`](https://pypi.org/project/simplibs-markdown/) (the Markdown output),
[`simplibs-cli`](https://pypi.org/project/simplibs-cli/),
[`simplibs-logger`](https://pypi.org/project/simplibs-logger/) and
[`simplibs-style`](https://pypi.org/project/simplibs-style/) (the command line),
[`simplibs-validate`](https://pypi.org/project/simplibs-validate/) and
[`simplibs-exception`](https://pypi.org/project/simplibs-exception/).

A language **add-on** is installed the same way — `pip install simplibs-code-extractor` — and its
profiles show up on their own in `simplibs-extractor --list-systems`. Nothing needs to be imported. From
Python, call `load_plugins()` once before you look a profile up — the command does that for you.

The text steps used in the examples below come from
[`simplibs-text`](https://pypi.org/project/simplibs-text/), which is **not** a dependency of the extractor:
`pip install simplibs-text` when you want them.

---

## 🚀 Quick Start in 60 Seconds

### Level 1: The command line

```bash
simplibs-extractor generic/all my_project                 # every text file, unchanged -> my_project/extraction.md
simplibs-extractor generic/all my_project --dry-run       # plan and report, write nothing
simplibs-extractor generic/all my_project -o out --format plain --no-tree
simplibs-extractor --list-systems                         # what is installed
simplibs-extractor --list-profiles python                 # the profiles of one system (an add-on's)
simplibs-extractor python code-clean,data-all my_project  # two profiles -> two files, one run
simplibs-extractor                                        # in a terminal: asks for what is missing
```

The result of the first command is a Markdown document (the paths are shown as inline code, a
fenced block per file, the fence always longer than any backticks inside the code):

````markdown
<!-- simplibs-extractor:generated -->

# Extraction: my_project

Profile: `generic/all`

```text
├── src/
│   ├── app.py
│   └── config.py
├── tests/
│   └── test_app.py
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

def main():
    # greet
    print("hi")  # inline
```
````

The command ends with an **exit code**: `0` everything succeeded, `1` some extraction failed or
selected nothing, `2` the command was refused before anything ran (a typo in a profile, a missing
source with nobody to ask).

### Level 2: From Python

```python
from simplibs.extractor import extract, format_summary

result = extract(source="my_project", dry_run=True)    # everything is a keyword; a typo is refused: extract(sourse=...)

result.success                                          # -> True
[f.relative for f in result.ok_files]                   # -> ['README.md', 'src/app.py', 'src/config.py', 'tests/test_app.py']
[(f.relative, f.reason) for f in result.skipped_files]  # -> [('logo.png', 'not a text file')]
result.tokens_estimate                                  # -> 115     a rough guess: characters / 4
print(format_summary(result))                           # the same text the command prints
```

A ready `ExtractionConfig` can be reused with one change — keywords change a copy of it:

```python
from simplibs.extractor import ExtractionConfig, extract

config = ExtractionConfig(source="my_project", overwrite="unique", max_file_size=200_000)
extract(config)                                         # my_project/extraction.md
extract(config, dry_run=True, add_tree=False)           # the same, changed for this call only
```

### Level 3: Your own profile

A **profile** is a name for "which files, how to clean them, what the output is called": rules on the
relative path plus **steps** that transform each file's text (any `Action` — the text steps of
[`simplibs-text`](https://pypi.org/project/simplibs-text/) fit directly).

```python
import re
from simplibs.extractor import Profile, extract, register_profile
from simplibs.path.rules import HasSuffix, ParentNameIs
from simplibs.text.actions import RemoveMatches
from simplibs.text.presets import COMPACT

register_profile(Profile(
    system="python", name="code-clean",
    description="Python sources without comments and blank lines.",
    include=HasSuffix(".py"),                                   # a rule on the path inside the source
    exclude=ParentNameIs("tests"),                              # a file directly in a folder named tests
    steps=RemoveMatches(pattern=re.compile(r"#.*")) >> COMPACT,  # one Action for every file
    output_name="python_clean.md",
))

result = extract(source="my_project", profile="python/code-clean")
[(f.relative, f.bytes_in, f.bytes_out) for f in result.ok_files]
# -> [('src/app.py', 62, 38), ('src/config.py', 10, 10)]     what the profile saved, file by file
```

`steps` may also be a mapping `suffix -> Action` (`{".py": clean_python, ".md": keep_text, "*": other}`),
because a step sees only the text, never the path — a profile that cleans two languages needs two
pipelines. Rules may be combined with `&`, `|` and `~`; `include` and `exclude` of a single `extract`
call narrow the profile's.

### Level 4: Scripts, batches, formats and add-ons

```python
# extract_here.py — dropped into a project folder (or: simplibs-extractor init my_project)
from simplibs.extractor import extract_here

extract_here(__file__, profile="python/code-clean")     # source = this folder, output next to the script,
                                                        # the script itself is never part of the output
```

```python
from simplibs.extractor import GENERATED_MARKER, ExtractionConfig, extract, extract_many, register_renderer

configs = [ExtractionConfig(source="my_project", profile=key) for key in ("python/code-clean", "generic/all")]
results = extract_many(configs)                         # a broken config is a result with `fatal`, the others still run

def render_names(entries, context):                     # a new output format is a function: entries in, text out
    names = "\n".join(entry.relative for entry in entries)
    return f"# {GENERATED_MARKER}\n{names}\n"            # the marker keeps the output out of the next run

register_renderer("names", render_names)
extract(source="my_project", format="names", target="my_project/files.txt")
```

An **add-on** announces itself in its own `pyproject.toml`, and the extractor finds it without
importing it by name:

```toml
[project.entry-points."simplibs.extractor.plugins"]
code = "simplibs.code_extractor:register_all"            # a function with no arguments that registers profiles
```

The command loads add-ons itself; from Python, `load_plugins()` does it (`extract()` never loads add-ons on its own).

---

## 🔬 The six phases

```
 Select ──► Read ──► Transform ──► Render ──► Write ──► Report
 which       text or   steps of     one        atomic,    an ExtractionResult,
 files       skipped?  the profile  document   policy      a summary, an exit code
```

| Phase         | What it does                                                                                                                  | Never does                                  |
|---------------|-------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------|
| **Select**    | Scans the folder (without ignored names), drops the target and `skip_paths`, applies `include` (AND) and `exclude` (OR) to the **relative** path | reads a file's content                      |
| **Read**      | Per file, cheapest check first: binary → generated by us → too large → read; reports `skipped` or `error` and never raises for a file | decides which files are taken               |
| **Transform** | Runs the profile's steps on the text (the action of the file's suffix, or the one for all); a step that fails marks **that file** `error` | sees a path, only the text                  |
| **Render**    | Turns the entries into one text through the renderer of the format; writes the marker, the title and the tree                  | touches the disk                            |
| **Write**     | `overwrite`, `unique`, `backup` or `error`; a dry run decides the same and stops; the write itself is atomic                  | writes in a dry run                         |
| **Report**    | Builds the `ExtractionResult`: per-file reports, sizes, a token estimate, success                                             | prints (the command and scripts do)         |

Two kinds of failure, two behaviours. A **configuration that cannot run** (a missing source, an
unknown profile or format, an unknown parameter) raises a card before any file is read. A **file that
cannot be used** is a line in the result. A **write that fails** raises, because then there is no
output at all. An extraction that selected nothing writes nothing and counts as **unsuccessful**: it is
almost always a wrong filter or a wrong folder, and a file with just a title would hide it.

➡️ [README_EXTRACTOR_RUN](https://github.com/simplibs/simplibs-extractor/blob/main/docs/logic/README_EXTRACTOR_RUN.md) · [SELECT](https://github.com/simplibs/simplibs-extractor/blob/main/docs/logic/README_EXTRACTOR_SELECT.md) · [READ](https://github.com/simplibs/simplibs-extractor/blob/main/docs/logic/README_EXTRACTOR_READ.md) · [TRANSFORM](https://github.com/simplibs/simplibs-extractor/blob/main/docs/logic/README_EXTRACTOR_TRANSFORM.md) · [RENDER](https://github.com/simplibs/simplibs-extractor/blob/main/docs/logic/README_EXTRACTOR_RENDER.md) · [WRITE](https://github.com/simplibs/simplibs-extractor/blob/main/docs/logic/README_EXTRACTOR_WRITE.md) · [REPORT](https://github.com/simplibs/simplibs-extractor/blob/main/docs/logic/README_EXTRACTOR_REPORT.md)

---

## 🛠️ Architecture & Package Structure

```
src/simplibs/extractor/
├── annotations/          ◄── FileStatus, OutputFormat, OverwritePolicy, StepsSpec
├── constants/            ◄── DEFAULT_*, GENERATED_MARKER, LANGUAGE_BY_SUFFIX, PLUGIN_GROUP, SCRIPT_TEMPLATE, ...
├── definitions/          ◄── Frozen dataclasses: ExtractionConfig, Profile, ExtractionResult, FileReport, Entry
├── registry/             ◄── Profiles and renderers by name: register_*, get_*, list_*, expand_profile_keys
├── logic/                ◄── The six phases and the run
│   ├── select/  read/  transform/  render/  write/  report/
│   ├── extract.py  extract_many.py  failure_result.py   ◄── The run: the phases put together
│   └── _common/  _helpers/                              ◄── Private helpers of the phases and of the run
├── plugins/              ◄── load_plugins: add-ons found through entry points
├── scripts/              ◄── extract_here, generate_local_script
├── cli/                  ◄── The command (not imported by the package root)
├── __main__.py           ◄── python -m simplibs.extractor
└── py.typed
```

Folders named `_validations/`, `_helpers/` and `_common/` are private: they hold the functions that raise the
library's error cards and the small helpers of the code next to them.

Everything a program needs is importable from `simplibs.extractor`. The command line is the one
exception: `from simplibs.extractor.cli import run_cli` — so a program that only calls `extract()` does
not load the prompt and logger libraries it never uses. **Importing the package has two side effects**:
the profile `generic/all` and the formats `markdown` and `plain` are registered. Nothing else happens
until a function is called; add-ons are looked up only by `load_plugins()` (which the command calls).

---

## 🏃 Running an extraction

| Function        | Description / Parameters                                                                                                    |
|-----------------|-----------------------------------------------------------------------------------------------------------------------------|
| `extract`       | One extraction through all six phases (`config=None`, keyword-only: `logger=None`, and any field of `ExtractionConfig` as a keyword). Returns an `ExtractionResult`. |
| `extract_many`  | Several extractions in a row; a run that cannot start or write appears as a result with `fatal` set and does not stop the others (`configs`, keyword-only: `logger=None`, `stop_on_error=False`). |

Progress goes to the `logger` you pass — a `SimpleLogger`, a standard `logging.Logger` or nothing —
and never to the screen.

➡️ [README_EXTRACTOR_RUN](https://github.com/simplibs/simplibs-extractor/blob/main/docs/logic/README_EXTRACTOR_RUN.md)

---

## 📜 `scripts/` — Two lines in a folder

| Function                | Description / Parameters                                                                                              |
|-------------------------|-----------------------------------------------------------------------------------------------------------------------|
| `extract_here`          | Extracts the folder a script lies in into a file next to it; the script itself is left out (`anchor`, `profile=None`, keyword-only: `output_name=None`, `quiet=False`, `logger=None`, any `ExtractionConfig` field). Prints the summary unless `quiet`. |
| `generate_local_script`  | Writes a ready-to-run `extract_here.py` (`path`, `profile=None`, keyword-only: `overwrite=False`); only the profile's **key** is stored. |

➡️ [README_EXTRACTOR_SCRIPTS](https://github.com/simplibs/simplibs-extractor/blob/main/docs/README_EXTRACTOR_SCRIPTS.md)

---

## 🧩 Profiles, registry and add-ons

| Function               | Description / Parameters                                                                                          |
|------------------------|-------------------------------------------------------------------------------------------------------------------|
| `register_profile`     | Adds a profile under its `system/name` key and returns it (`profile`, keyword-only: `replace_existing=False`).     |
| `get_profile`          | The profile of a key, or a `NotFoundError` card that lists the registered keys (`key`).                            |
| `list_profiles`        | The registered profiles, sorted by key; a new list (`system=None`).                                                |
| `list_systems`         | The systems that have at least one profile, sorted.                                                                |
| `expand_profile_keys`  | Turns what a person typed into full keys: `("python", "a,b")` → `["python/a", "python/b"]` (`system`, `names`).    |
| `register_renderer`    | Adds an output format: a function `(entries, context) -> str` (`name`, `func`, keyword-only: `replace_existing=False`). |
| `get_renderer`         | The renderer of a format, or a card listing the known formats (`name`).                                            |
| `list_formats`         | The registered output formats, sorted.                                                                             |
| `load_plugins`         | Lets every installed add-on register its profiles; returns `(loaded, failed)` and never lets one add-on stop another (keyword-only: `group`, `entry_points`). |

➡️ [README_EXTRACTOR_REGISTRY](https://github.com/simplibs/simplibs-extractor/blob/main/docs/README_EXTRACTOR_REGISTRY.md) · [README_EXTRACTOR_PLUGINS](https://github.com/simplibs/simplibs-extractor/blob/main/docs/README_EXTRACTOR_PLUGINS.md) (writing an add-on)

---

## 📦 `definitions/` — Data objects

| Class              | Description                                                                                                               |
|--------------------|---------------------------------------------------------------------------------------------------------------------------|
| `ExtractionConfig` | Everything one run needs: `source`, `target`, `profile`, `include`, `exclude`, `ignore_names`, `recursive`, `format`, `overwrite`, `dry_run`, `max_file_size`, `add_tree`, `title`, `skip_paths`. Frozen and validated. |
| `Profile`          | A named set of selection rules and steps: `system`, `name`, `description`, `include`, `exclude`, `steps`, `output_name`, `format`; `key` is `"system/name"`. Frozen and validated when built. |
| `ExtractionResult` | The outcome of one run: `config`, `profile_key`, `target`, `written`, `dry_run`, `files`, `bytes_in`, `bytes_out`, `tokens_estimate`, `duration`, `fatal`; properties `ok_files`, `skipped_files`, `error_files`, `success`. |
| `FileReport`       | What happened to one file: `path`, `relative`, `status` (`ok`, `skipped`, `error`), `reason`, `bytes_in`, `bytes_out`. |
| `Entry`            | One file ready to be rendered: `relative`, `suffix`, `text`.                                                               |

`bytes_out` of an `ExtractionResult` is the size of the whole **rendered output** (title, tree and fences
included); the `bytes_out` of a `FileReport` is the size of that file's text **after the steps** — so the
report shows what a profile saves, file by file. `RenderContext`, the other object a renderer receives, is
described with the [output formats](#-output-formats).

➡️ [README_EXTRACTOR_DEFINITIONS](https://github.com/simplibs/simplibs-extractor/blob/main/docs/README_EXTRACTOR_DEFINITIONS.md)

---

## 🖨️ Output formats

Two formats are built in, registered through the same door as any later one (the core never branches
on a format name). Both start with the **marker** `simplibs-extractor:generated` in their first
lines, which is how an output is recognised — whatever it is called — when it lies in a scanned folder.
**A renderer of your own should write the marker too** (`GENERATED_MARKER`, in its first three lines), or its output would be read back as input on the next run.

| Format     | What it looks like                                                                                                                  |
|------------|-------------------------------------------------------------------------------------------------------------------------------------|
| `markdown` | A comment with the marker, a title, `Profile: ...`, an optional tree, then `## `path`` and a fenced block per file with the language of its suffix. The default. |
| `plain`    | `# simplibs-extractor:generated`, `# <title>`, `# profile: ...`, an optional `# TREE`, then `# FILE: path` followed by the text — the layout of the old code extractor. |

| Helper           | Description                                                                                       |
|------------------|---------------------------------------------------------------------------------------------------|
| `RenderContext`  | What a renderer receives besides the entries: `title`, `source`, `profile_key`, `add_tree` (exported from the package root, like `Entry`). |
| `build_tree`     | Draws a directory tree from relative paths, folders first (`from simplibs.extractor.logic import build_tree`). |
| `estimate_tokens` | A **rough** token count: characters / `chars_per_token` (default 4), rounded up. No model name, no tokenizer. |
| `format_summary` | The readable text of an `ExtractionResult`: counts, sizes, errors first (`result`, keyword-only: `max_listed=10`). |

➡️ [README_EXTRACTOR_RENDER](https://github.com/simplibs/simplibs-extractor/blob/main/docs/logic/README_EXTRACTOR_RENDER.md) · [README_EXTRACTOR_REPORT](https://github.com/simplibs/simplibs-extractor/blob/main/docs/logic/README_EXTRACTOR_REPORT.md)

---

## ⌨️ The command line

```
simplibs-extractor [SYSTEM] [PROFILES] [SOURCE] [-o FOLDER] [--format NAME] [--overwrite POLICY]
                   [--no-tree] [--dry-run] [-q] [-v | -vv] [--no-color]
simplibs-extractor --list-systems | --list-profiles SYSTEM
simplibs-extractor init [DIRECTORY] [--profile KEY] [--force]
```

| Option                | Meaning                                                                                                       |
|-----------------------|---------------------------------------------------------------------------------------------------------------|
| `SYSTEM PROFILES`     | `python code-clean,data-all`, or full keys: `python/code-clean`, `generic/all,python/data-all`. Several profiles are several runs and several files. |
| `SOURCE`              | The folder to extract from. A first word that is a folder and not a known profile is taken as the source: `simplibs-extractor ./src`. |
| `-o`, `--output`      | The output **folder** (default: the source). The file name always comes from the profile.                      |
| `--format`            | An output format; the choices are the registered ones. Default: the profile's.                                 |
| `--overwrite`         | `overwrite` (default), `unique`, `backup` or `error`.                                                          |
| `--no-tree`           | Leave the directory tree out of the output.                                                                    |
| `--dry-run`           | Plan and report, write nothing.                                                                                |
| `-q`, `-v`, `-vv`     | Only errors / more detail / everything; `--no-color` for plain text.                                           |
| `--list-systems`, `--list-profiles SYSTEM` | Answered from the registry; nothing is extracted. An unknown system is an error, not an empty list. |
| `init`                | Writes a local `extract_here.py` (refuses to replace one without `--force`).                                   |

What is missing is asked for in a terminal (the system, then the profiles, then the source; a dry-run
question only to a person who is already being asked). Without a terminal the same situation is a
**card** that names the missing argument — a CI job never hangs. Add-ons that fail to load are
reported as a warning and do not stop the command.

| Exit code | Meaning                                                                                              |
|-----------|------------------------------------------------------------------------------------------------------|
| `0`       | Everything succeeded.                                                                                |
| `1`       | Some extraction failed, an `error` file occurred, or nothing was selected.                           |
| `2`       | The command was refused before anything ran: a mistyped profile, a missing source with nobody to ask, two profiles that would write the same file, an unknown option. |

➡️ [README_EXTRACTOR_CLI](https://github.com/simplibs/simplibs-extractor/blob/main/docs/README_EXTRACTOR_CLI.md)

---

## 🏷️ `annotations/` and `constants/`

| Name                  | Kind           | Description                                                                                          |
|-----------------------|----------------|------------------------------------------------------------------------------------------------------|
| `FileStatus`          | Literal        | `"ok"`, `"skipped"` or `"error"`.                                                                    |
| `OutputFormat`        | Annotated type | The **name** of a format: lowercase, starts with a letter (`"markdown"`, `"json-manifest"`). Whether a renderer exists is checked when the config is resolved. |
| `OverwritePolicy`     | Literal        | `"overwrite"`, `"unique"`, `"backup"` or `"error"`.                                                  |
| `StepsSpec`           | Type alias     | `None`, one `Action`, or a mapping `suffix -> Action` (the key `"*"` is the fallback).               |
| `DEFAULT_PROFILE_KEY` | Constant       | `"generic/all"`, the built-in profile: every text file, unchanged.                                   |
| `GENERATED_MARKER`    | Constant       | `"simplibs-extractor:generated"`, the text that marks an output.                                     |

The other constants (`DEFAULT_MAX_FILE_SIZE` = 1 MB, `DEFAULT_OUTPUT_NAME` = `"extraction.md"`,
`DEFAULT_SCRIPT_NAME`, `LANGUAGE_BY_SUFFIX`, `MARKER_SCAN_LINES` = 3, `PLUGIN_GROUP`,
`SCRIPT_TEMPLATE`) are documented in the reference below and importable from `simplibs.extractor.constants`.

➡️ [README_EXTRACTOR_ANNOTATIONS](https://github.com/simplibs/simplibs-extractor/blob/main/docs/README_EXTRACTOR_ANNOTATIONS.md) · [README_EXTRACTOR_CONSTANTS](https://github.com/simplibs/simplibs-extractor/blob/main/docs/README_EXTRACTOR_CONSTANTS.md)

---

## ⚠️ Exceptions

The library defines no exceptions of its own. A wrong call is a structured
[`simplibs.exception`](https://pypi.org/project/simplibs-exception/) card with a name starting with
`EXTRACTOR_`; a caller that wants "any error of this library" catches `SimpleError`. Problems of
**single files** (a read that fails, a step that raises) are not exceptions at all — they are
`error` lines in the result.

| Error name                     | Class                | Wraps                | Raised when                                                                  |
|--------------------------------|----------------------|----------------------|------------------------------------------------------------------------------|
| `EXTRACTOR_CONFIG_INVALID`     | `ParamError`         | `ValueError`         | An unknown config parameter, a missing `source`, an unknown output format, a bad `output_name` or script name, a renderer name that is taken, `chars_per_token <= 0`, unusable command-line arguments |
| `EXTRACTOR_PROFILE_EXISTS`     | `AlreadyExistsError` | `ValueError`         | `register_profile` gets a key that is registered and `replace_existing` is `False` |
| `EXTRACTOR_PROFILE_INVALID`    | `ParamError`         | `ValueError`         | A `Profile` is built with an unusable system, name, `output_name` or `steps` key; `expand_profile_keys` gets a name without a system, or nothing |
| `EXTRACTOR_PROFILE_NOT_FOUND`  | `NotFoundError`      | `LookupError`        | A profile key is not registered (the card lists the registered ones)          |
| `EXTRACTOR_SOURCE_NOT_FOUND`   | `NotFoundError`      | `FileNotFoundError`  | The source is not an existing directory                                       |
| `EXTRACTOR_STEP_RESULT_INVALID` | `OperationError`    | `TypeError`          | A step returned something other than a `str` — reported against **that file** |
| `EXTRACTOR_TARGET_EXISTS`      | `AlreadyExistsError` | `FileExistsError`    | The output exists and the policy is `error` (also in a dry run)               |
| `EXTRACTOR_TARGET_IS_DIR`      | `StateError`         | `IsADirectoryError`  | The output path is an existing directory                                      |

A write that fails for other reasons raises the cards of
[`simplibs-file`](https://pypi.org/project/simplibs-file/) (`AccessError`, `ConversionError`), and a
missing terminal the card of [`simplibs-cli`](https://pypi.org/project/simplibs-cli/)
(`CLI_NOT_INTERACTIVE`).

What is an exception and what is not:

| Situation                                                                       | How it is reported                                                   |
|---------------------------------------------------------------------------------|----------------------------------------------------------------------|
| A **wrong call** — a typo in a parameter, an unknown profile, a missing folder  | a card with an `EXTRACTOR_` name, **raised**                         |
| A problem of **one file** — a read that fails, a step that raises               | **not raised**: the file is `error` in the result, the run continues |
| A run that cannot start or cannot write, inside `extract_many`                  | **not raised**: a result with `fatal` set, the other runs continue   |
| A wrong **type** of a parameter or a field (`overwrite="clobber"`, `format=5`)  | a `ValidationError` from `simplibs-validate`                         |

Only the card — its class and its `EXTRACTOR_` name — is part of the interface. The functions that raise
it are private; each lives in a `_validations/` folder next to the code that uses it.

---

## 📚 Documentation

The detailed references — every function and class with its parameters, return value, raised errors, an
example and a look under the hood:

| Reference | What it describes |
|-----------|-------------------|
| [ANNOTATIONS](https://github.com/simplibs/simplibs-extractor/blob/main/docs/README_EXTRACTOR_ANNOTATIONS.md) | `FileStatus`, `OutputFormat`, `OverwritePolicy`, `StepsSpec` |
| [CONSTANTS](https://github.com/simplibs/simplibs-extractor/blob/main/docs/README_EXTRACTOR_CONSTANTS.md) | the fixed values: limits, names, the marker, the script template |
| [DEFINITIONS](https://github.com/simplibs/simplibs-extractor/blob/main/docs/README_EXTRACTOR_DEFINITIONS.md) | `ExtractionConfig`, `Profile`, `ExtractionResult`, `FileReport`, `Entry` |
| [REGISTRY](https://github.com/simplibs/simplibs-extractor/blob/main/docs/README_EXTRACTOR_REGISTRY.md) | profiles and output formats by name |
| [SELECT](https://github.com/simplibs/simplibs-extractor/blob/main/docs/logic/README_EXTRACTOR_SELECT.md) · [READ](https://github.com/simplibs/simplibs-extractor/blob/main/docs/logic/README_EXTRACTOR_READ.md) · [TRANSFORM](https://github.com/simplibs/simplibs-extractor/blob/main/docs/logic/README_EXTRACTOR_TRANSFORM.md) | phases 1–3: which files, what is in them, cleaning the text |
| [RENDER](https://github.com/simplibs/simplibs-extractor/blob/main/docs/logic/README_EXTRACTOR_RENDER.md) · [WRITE](https://github.com/simplibs/simplibs-extractor/blob/main/docs/logic/README_EXTRACTOR_WRITE.md) · [REPORT](https://github.com/simplibs/simplibs-extractor/blob/main/docs/logic/README_EXTRACTOR_REPORT.md) | phases 4–6: the document, the disk, the report |
| [RUN](https://github.com/simplibs/simplibs-extractor/blob/main/docs/logic/README_EXTRACTOR_RUN.md) | `extract`, `extract_many` — putting the phases together |
| [PLUGINS](https://github.com/simplibs/simplibs-extractor/blob/main/docs/README_EXTRACTOR_PLUGINS.md) | finding add-ons, and writing one |
| [SCRIPTS](https://github.com/simplibs/simplibs-extractor/blob/main/docs/README_EXTRACTOR_SCRIPTS.md) | `extract_here`, `generate_local_script` |
| [CLI](https://github.com/simplibs/simplibs-extractor/blob/main/docs/README_EXTRACTOR_CLI.md) | the command `simplibs-extractor` |

---

## 🔗 Related libraries

* **[`simplibs-text`](https://pypi.org/project/simplibs-text/)** — the text steps (`RemoveMatches`, `COMPACT`, `KeepLineRange`, ...) a profile's `steps` are made of.
* **`simplibs-code-extractor`** — the first add-on: profiles for Python and React projects, built on this extractor.
* **[`simplibs-path`](https://pypi.org/project/simplibs-path/)** — scanning, normalized paths and the path rules (`HasSuffix`, `ParentNameIs`, ...) behind `include` and `exclude`.
* **[`simplibs-file`](https://pypi.org/project/simplibs-file/)** — the atomic write, the backup, the text check and the size.
* **[`simplibs-rules`](https://pypi.org/project/simplibs-rules/)** and **[`simplibs-actions`](https://pypi.org/project/simplibs-actions/)** — the `Rule` and `Action` objects a profile is made of.
* **[`simplibs-markdown`](https://pypi.org/project/simplibs-markdown/)** — builds the Markdown output.
* **[`simplibs-cli`](https://pypi.org/project/simplibs-cli/)**, **[`simplibs-logger`](https://pypi.org/project/simplibs-logger/)** and **[`simplibs-style`](https://pypi.org/project/simplibs-style/)** — the prompts, the logger and the colors of the command.
* **[`simplibs-validate`](https://pypi.org/project/simplibs-validate/)** and **[`simplibs-exception`](https://pypi.org/project/simplibs-exception/)** — the validation and the error cards.

---

## ☯️ About simplibs

All libraries in the **simplibs** (Simple Libraries) ecosystem share a common
engineering philosophy:

* **Dyslexia-friendly:**
We actively minimize cognitive load. Code is atomized into small, self-contained units,
files are named directly after the logical task they perform, and explanations describe
*why* something is designed, not just *what* it is.
* **Programmer's Zen:**
Nothing should be missing, and nothing should be superfluous. We value clean execution
paths and robust, understandable code architectures over rushed, messy feature sets.
* **Defensive Style:**
We actively anticipate edge cases and failure modes so that only safe operational paths
remain. Our code is built to degrade gracefully rather than crash unexpectedly.
* **Minimalism:**
Find the most direct path to the goal in as few operational steps as possible without
taking shortcuts on safety, readability, or completeness.
* **Code as Craft:**
Code should be pleasant to look at, readable at a glance, and evoke structural harmony.
We treat software engineering as a precision trade.

---

### 🤝 Contributing & Community

This is an **open-source project** built with love and care. We strongly believe in
community collaboration and welcome any feedback, bug reports, or feature ideas!

* **Want to contribute?** Feel free to open an Issue or submit a Pull Request.
* **Want to get in touch?** If you'd like to discuss the project further, collaborate,
  or just say hello, feel free to open a GitHub Issue or start a Discussion.

---

### 📝 License

This library is released under the **MIT License**. Build great things!

---
