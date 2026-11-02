# 📦 `definitions` — Data Objects

The `definitions` package holds the **data objects** the whole library passes around: what you describe a run
with (`ExtractionConfig`, `Profile`), what a run hands back (`ExtractionResult`, `FileReport`) and what flows
between its phases (`Entry`, `Resolved`). They contain data and a few small properties — no logic of their
own.

```python
from simplibs.extractor import Entry, ExtractionConfig, ExtractionResult, FileReport, Profile
```

All of them are **frozen dataclasses** (`frozen=True, slots=True`): once built, an object never changes, so a
registered profile can be shared by every run and a result can be passed around without anyone altering it.
A changed copy is made with `dataclasses.replace`:

```python
import dataclasses
from simplibs.extractor import ExtractionConfig

config = ExtractionConfig(source="my_project")
quiet = dataclasses.replace(config, dry_run=True, add_tree=False)       # a new object; `config` is untouched

config.dry_run = True                                                   # raises FrozenInstanceError
```

## Two kinds of object

| Kind                    | Objects                                                  | Built by          | Checked by                        |
|-------------------------|----------------------------------------------------------|-------------------|-----------------------------------|
| **Input** (you write it)| `ExtractionConfig`, `Profile`                            | **you**           | `@validate_dataclass` — every field is type-checked when the object is built |
| **Output** (it is made) | `ExtractionResult`, `FileReport`, `Entry`, `Resolved`    | **the library**   | not validated — the library builds them itself |

Input is checked because it comes from outside: a mistake fails **when the object is built**, with a
`ValidationError` naming the field, and not at the first run that happens to use it. The output objects are
built by code that already knows what it is doing, so they stay plain dataclasses.

> **What an object cannot check.** A type cannot say that a folder exists or that a profile key is
> registered. `ExtractionConfig(source="no_such_folder")` is a valid object; the folder is checked when the run
> **resolves** the configuration (`EXTRACTOR_SOURCE_NOT_FOUND`). `Profile` is the exception — it checks the
> characters of its key, its output name and its steps keys itself, because a profile that can never work
> should never exist.

## How they fit together

```
ExtractionConfig ──┐
 (or keywords)     ├─►  Resolved  ──►  Select ──►  Read ──►  Transform ──►  Render ──►  Write
Profile (or key) ──┘                                  │            │            ▲
                                                      ▼            ▼            │
                                                 FileReport    FileReport     Entry
                                                      └────────────┴──► ExtractionResult
```

`Resolved` is the configuration after every default has been filled in; each phase after it reads from it.
Every file leaves the read and transform phases as a `FileReport` and — if it is included — an `Entry`.
`ExtractionResult` gathers the reports.

`Entry` and the other objects of the **render** phase (`RenderContext`) are exported from the package root;
`Resolved` is internal and is imported from `simplibs.extractor.definitions`.

---

## 🧭 Table of Contents

**What you describe a run with**

* [`ExtractionConfig`](#extractionconfig)
* [`Profile`](#profile)

**What a run hands back**

* [`ExtractionResult`](#extractionresult)
* [`FileReport`](#filereport)

**What flows between phases**

* [`Entry`](#entry)
* [`Resolved`](#resolved)

[⬅️ Back to main README](../README.md#-definitions--data-objects)

---

### `ExtractionConfig`

**Everything one extraction needs to know** — the single input of `extract()`.

**Parameters:**

| Name            | Type                          | Default       | Description                                                                                          |
|-----------------|-------------------------------|---------------|------------------------------------------------------------------------------------------------------|
| `source`        | `PathLike`                    | *(required)*  | The folder to extract from.                                                                          |
| `target`        | `PathLike \| None`            | `None`        | The output **file**; `None` means `source / profile.output_name`.                                    |
| `profile`       | `Profile \| str \| None`      | `None`        | A `Profile`, a registered key (`"python/code-clean"`), or `None` for `generic/all`.                  |
| `include`       | `Rule \| None`                | `None`        | A rule on the path relative to the source, combined with the profile's by **AND**.                   |
| `exclude`       | `Rule \| None`                | `None`        | A rule on the path relative to the source, combined with the profile's by **OR**.                    |
| `ignore_names`  | `frozenset[str] \| None`      | `None`        | Folder and file names the scan skips; `None` means the default set (see below).                      |
| `recursive`     | `bool`                        | `True`        | Whether sub-folders are scanned.                                                                     |
| `format`        | `OutputFormat \| None`        | `None`        | The output format; `None` means the profile's.                                                       |
| `overwrite`     | `OverwritePolicy`             | `"overwrite"` | What happens when the output exists.                                                                 |
| `dry_run`       | `bool`                        | `False`       | Plan everything, write nothing.                                                                      |
| `max_file_size` | `ByteCount \| None`           | `1_000_000`   | Larger files are skipped; `None` switches the limit off.                                             |
| `add_tree`      | `bool`                        | `True`        | Whether the output starts with a directory tree.                                                     |
| `title`         | `str \| None`                 | `None`        | The heading of the output; `None` means `Extraction: <source folder name>`.                          |
| `skip_paths`    | `tuple[PathLike, ...]`        | `()`          | Extra files that never enter the extraction (for example an embedded script).                        |

**Returns:** a frozen `ExtractionConfig`.

**Raises:**
`ValidationError` — a field has the wrong type or value (`overwrite="clobber"`, `max_file_size=0`,
`include=[...]` instead of a `Rule`).

**Example usage:**

```python
from simplibs.extractor import ExtractionConfig, extract
from simplibs.path.rules import HasSuffix, ParentNameIs

config = ExtractionConfig(source="my_project")                  # only `source` is required
config.overwrite                                                # -> 'overwrite'
config.max_file_size                                            # -> 1000000
config.target                                                   # -> None     decided later, by the profile

config = ExtractionConfig(
    source="my_project",
    profile="python/code-clean",
    include=HasSuffix(".py"),
    exclude=ParentNameIs("tests"),
    overwrite="unique",
    max_file_size=200_000,
)

extract(config)                                                 # one run
extract(config, dry_run=True, add_tree=False)                   # the same config, changed for this call only

ExtractionConfig(source="my_project", overwrite="clobber")      # raises ValidationError
ExtractionConfig(source="my_project", max_file_size=0)          # raises ValidationError — never a limit of zero bytes
ExtractionConfig(source="my_project", include=[HasSuffix(".py")])   # raises ValidationError — one Rule, not a list
```

**One rule, not a list.** `include` and `exclude` are single `Rule` objects; you compose them with `&`, `|`
and `~` (`HasSuffix(".py") & ~ParentNameIs("tests")`). A list would leave open whether its items combine by AND
or by OR.

**A config can only narrow a profile.** `include` is combined with the profile's by **AND** and `exclude` by
**OR**, so a config never selects a file the profile has already left out. To widen a selection, use a
different profile.

**What the scan skips by default.** `ignore_names=None` means the housekeeping names of `simplibs-path`
(version-control and cache folders and the like) **plus** the draft files of `SafeFileWriter`. A set you give
**replaces the default completely** — it is not added to it.

**Raw values.** `source`, `target` and `profile` are stored **as given**. Normalizing them and looking the
profile up is the job of [`resolve_config`](logic/README_EXTRACTOR_SELECT.md), which returns a
[`Resolved`](#resolved).

<details>
<summary>🔍 Under the hood</summary>

```python
@validate_dataclass
@dataclass(frozen=True, slots=True)
class ExtractionConfig:
    source: PathLike
    target: PathLike | None = None
    profile: Profile | str | None = None
    include: Rule | None = None
    exclude: Rule | None = None
    ignore_names: frozenset[str] | None = None
    recursive: bool = True
    format: OutputFormat | None = None
    overwrite: OverwritePolicy = "overwrite"
    dry_run: bool = False
    max_file_size: ByteCount | None = DEFAULT_MAX_FILE_SIZE
    add_tree: bool = True
    title: str | None = None
    skip_paths: tuple[PathLike, ...] = ()
```

`@validate_dataclass` sits **above** `@dataclass`, as its README requires: it wraps the `__init__` that
`@dataclass` has just generated.

The keywords of `extract()` are applied with `dataclasses.replace`, which is what lets a ready config be reused
with one change:

```python
# resolve_config
if config is None:
    config = ExtractionConfig(**overrides)
elif overrides:
    config = dataclasses.replace(config, **overrides)
```

The rules meet in the select phase:

```python
include = all_of(profile.include, config.include)       # AND — the config narrows
exclude = any_of(profile.exclude, config.exclude)       # OR  — the config adds exclusions
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `Profile`

**A named set of selection rules and transformation steps** — which files, how to clean them, what the output
is called. Registered under the key `"system/name"`.

**Parameters:**

| Name          | Type                  | Default           | Description                                                                              |
|---------------|-----------------------|-------------------|------------------------------------------------------------------------------------------|
| `system`      | `str`                 | *(required)*      | The family the profile belongs to (`"python"`, `"generic"`).                             |
| `name`        | `str`                 | *(required)*      | The name inside the family (`"code-clean"`).                                             |
| `description` | `str`                 | `""`              | One line shown by the listing commands.                                                  |
| `include`     | `Rule \| None`        | `None`            | A rule on the relative path; only matching files are taken.                              |
| `exclude`     | `Rule \| None`        | `None`            | A rule on the relative path; matching files are dropped.                                 |
| `steps`       | `StepsSpec`           | `None`            | How file text is transformed — nothing, one `Action`, or a mapping `suffix -> Action`.   |
| `output_name` | `str`                 | `"extraction.md"` | The file name of the output.                                                             |
| `format`      | `OutputFormat`        | `"markdown"`      | The output format.                                                                       |

**Returns:** a frozen `Profile`, with the property:

| Property | Type  | Description                                         |
|----------|-------|-----------------------------------------------------|
| `key`    | `str` | The registry key, `"system/name"`.                  |

**Raises:**
`ValidationError` — a field has the wrong type or value (`format="Markdown"`, a list instead of a `Rule`).
`ParamError` (`EXTRACTOR_PROFILE_INVALID`) — `system` or `name` is blank, padded, or contains `/`, `,` or
whitespace; `output_name` is not a portable file name; a key of a `steps` mapping is neither `"*"` nor a
lowercase suffix.

**Example usage:**

```python
import re
from simplibs.extractor import Profile, extract, register_profile
from simplibs.path.rules import HasSuffix, ParentNameIs
from simplibs.text.actions import RemoveMatches
from simplibs.text.presets import COMPACT

profile = Profile(
    system="python", name="code-clean",
    description="Python sources without comments and blank lines.",
    include=HasSuffix(".py"),                                   # rules judge the path inside the source
    exclude=ParentNameIs("tests"),
    steps=RemoveMatches(pattern=re.compile(r"#.*")) >> COMPACT,
    output_name="python_clean.md",
)

profile.key                                                     # -> 'python/code-clean'

register_profile(profile)                                       # now it can be chosen by its key
extract(source="my_project", profile="python/code-clean")
extract(source="my_project", profile=profile)                   # or passed directly, registered or not

Profile(system="py/thon", name="x")                             # raises ParamError — '/' cannot be a part of a key
Profile(system="python", name="x", output_name="out/a.md")      # raises ParamError — a file name, not a path
Profile(system="python", name="x", steps={"py": COMPACT})       # raises ParamError — "py" can never match a file
Profile(system="python", name="x", format="Markdown")           # raises ValidationError — wrong shape of a format name
```

A profile is **frozen** — a registered profile is shared by every run, and nobody may change it afterwards. A
variant is a new object:

```python
import dataclasses

minimal = dataclasses.replace(profile, name="code-minimal", output_name="python_min.md")
```

**Rules judge the path only.** `include` and `exclude` are evaluated on the path **relative to the source**,
so they must judge it by its text — suffix, name, folders. Anything that needs the disk (size, content) is the
business of the read phase, not of a profile's rules.

**Two layers of checking.** `@validate_dataclass` checks the **type** of every field, including the shape of
the format name. `__post_init__` adds what a type cannot say: the characters of a key part, a portable output
name and the keys of a steps mapping. A bad profile fails when it is built, not at the first run that uses it.

**The key.** A key is written `system/name`, and several keys travel in one command-line argument separated by
commas — that is why neither half may contain `/`, `,` or whitespace.

The built-in profile `generic/all` is a `Profile` with no rules and no steps; see
[the registry](README_EXTRACTOR_REGISTRY.md).

<details>
<summary>🔍 Under the hood</summary>

```python
@validate_dataclass
@dataclass(frozen=True, slots=True)
class Profile:
    system: str
    name: str
    description: str = ""
    include: Rule | None = None
    exclude: Rule | None = None
    steps: StepsSpec = None
    output_name: str = DEFAULT_OUTPUT_NAME
    format: OutputFormat = "markdown"

    def __post_init__(self) -> None:

        # 1. Both halves of the key must be usable in `system/name`
        for part_name, part in (("system", self.system), ("name", self.name)):
            if not is_key_part(part):
                raise_profile_key_part_error(part_name, part)

        # 2. The output name must be a portable file name
        if not is_valid_filename(self.output_name):
            raise_profile_output_name_error(self.output_name)

        # 3. A suffix mapping needs usable keys
        if isinstance(self.steps, Mapping):
            for suffix in self.steps:
                if not is_suffix_key(suffix):
                    raise_profile_steps_key_error(suffix)

    @property
    def key(self) -> str:
        return f"{self.system}/{self.name}"
```

The two private predicates:

```python
def is_key_part(value: str) -> bool:
    if not isinstance(value, str):
        return False
    if not value or value != value.strip():
        return False
    return not any(char in "/," or char.isspace() for char in value)

def is_suffix_key(value: str) -> bool:
    if not isinstance(value, str):
        return False
    if value == "*":
        return True
    return len(value) > 1 and value.startswith(".") and value == value.lower()
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `ExtractionResult`

**The outcome of one extraction** — the single source of every report. The command's summary, its exit code
and anything you build yourself are made from this one object; nothing is printed from inside the run.

**Attributes:**

| Name              | Type                     | Description                                                                         |
|-------------------|--------------------------|-------------------------------------------------------------------------------------|
| `config`          | `ExtractionConfig`       | The configuration the run started from.                                             |
| `profile_key`     | `str`                    | The key of the profile that was used.                                               |
| `target`          | `Path \| None`           | The output path (planned in a dry run, real otherwise); `None` if the run failed early. |
| `written`         | `bool`                   | Whether the output was actually written.                                            |
| `dry_run`         | `bool`                   | Whether the run only planned.                                                       |
| `files`           | `tuple[FileReport, ...]` | One report per file that was considered.                                            |
| `bytes_in`        | `int`                    | The total size of the original texts of the files that entered the output.          |
| `bytes_out`       | `int`                    | The size of the rendered output, in UTF-8 bytes.                                    |
| `tokens_estimate` | `int`                    | A rough token count of the rendered output.                                         |
| `duration`        | `float`                  | The run time in seconds.                                                            |
| `fatal`           | `str \| None`            | The reason the whole run stopped, or `None`.                                        |

**Properties:**

| Property         | Type                     | Description                                                              |
|------------------|--------------------------|--------------------------------------------------------------------------|
| `ok_files`       | `tuple[FileReport, ...]` | The files that entered the output, processed fully.                      |
| `partial_files`  | `tuple[FileReport, ...]` | The files that entered the output, but a step could not process them fully. |
| `skipped_files`  | `tuple[FileReport, ...]` | The files that were left out on purpose.                                 |
| `error_files`    | `tuple[FileReport, ...]` | The files that failed.                                                   |
| `success`        | `bool`                   | `True` if nothing failed and at least one file entered the output (whole or partial). |

**Returns (from `extract`):** one `ExtractionResult`. You rarely build one yourself.

**Example usage:**

```python
from simplibs.extractor import extract, format_summary

result = extract(source="my_project", dry_run=True)

result.success                                          # -> True
result.written, result.dry_run                          # -> (False, True)    planned, not written
result.target.name                                      # -> 'extraction.md'
result.profile_key                                      # -> 'generic/all'

[f.relative for f in result.ok_files]                   # -> ['README.md', 'src/app.py', 'src/config.py', 'tests/test_app.py']
[(f.relative, f.reason) for f in result.skipped_files]  # -> [('logo.png', 'not a text file')]
result.error_files                                      # -> ()
result.tokens_estimate                                  # -> 115     a rough guess: characters / 4

print(format_summary(result))                           # the same text the command prints
```

**A failed run is a result too.** Inside `extract_many`, a configuration that cannot start or cannot write
does not raise; it becomes a result with `fatal` set to a one-line reason, no files and `target=None`, and the
other runs continue:

```python
from simplibs.extractor import ExtractionConfig, extract_many

results = extract_many([ExtractionConfig(source="no_such_folder"), ExtractionConfig(source="my_project")])

results[0].success, results[0].target                   # -> (False, None)
results[0].fatal                                        # a one-line description of the failure
results[1].success                                      # -> True
```

**An extraction that selected nothing is unsuccessful.** It is almost always a wrong filter or a wrong folder,
so `success` is `False` even though nothing raised; nothing is written and `files` is empty.

**`bytes_out` is the whole document.** It measures the **rendered output** — title, tree and fences included —
and not the sum of the files' texts. What a profile saves **per file** is in the `bytes_in` and `bytes_out` of
each [`FileReport`](#filereport).

<details>
<summary>🔍 Under the hood</summary>

```python
@dataclass(frozen=True, slots=True)
class ExtractionResult:
    config: ExtractionConfig
    profile_key: str
    target: Path | None
    written: bool = False
    dry_run: bool = False
    files: tuple[FileReport, ...] = ()
    bytes_in: int = 0
    bytes_out: int = 0
    tokens_estimate: int = 0
    duration: float = 0.0
    fatal: str | None = None

    @property
    def ok_files(self) -> tuple[FileReport, ...]:
        return tuple(report for report in self.files if report.status == "ok")

    @property
    def partial_files(self) -> tuple[FileReport, ...]:
        return tuple(report for report in self.files if report.status == "partial")

    @property
    def skipped_files(self) -> tuple[FileReport, ...]:
        return tuple(report for report in self.files if report.status == "skipped")

    @property
    def error_files(self) -> tuple[FileReport, ...]:
        return tuple(report for report in self.files if report.status == "error")

    @property
    def success(self) -> bool:
        return self.fatal is None and not self.error_files and bool(self.ok_files or self.partial_files)
```

`extract` builds it at the end of the run:

```python
result = ExtractionResult(
    config=cfg,
    profile_key=profile.key,
    target=target,
    written=written,
    dry_run=cfg.dry_run,
    files=tuple(reports),
    bytes_in=sum(r.bytes_in for r in reports if r.status in ("ok", "partial")),
    bytes_out=len(rendered.encode("utf-8")),
    tokens_estimate=estimate_tokens(rendered),
    duration=time.perf_counter() - started,
)
```

and `failure_result` builds the one of a run that never started:

```python
return ExtractionResult(
    config=config,
    profile_key=key,
    target=None,
    dry_run=config.dry_run,
    fatal=describe_failure(error),
)
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `FileReport`

**What happened to one file** — one line of the report. A skipped or failed file keeps its **reason**, so "why
is my file missing?" always has an answer.

**Attributes:**

| Name        | Type             | Description                                                           |
|-------------|------------------|-----------------------------------------------------------------------|
| `path`      | `Path`           | The absolute path of the file.                                        |
| `relative`  | `str`            | The path relative to the source, with `/` separators.                 |
| `status`    | `FileStatus`     | `"ok"`, `"partial"`, `"skipped"` or `"error"`.                       |
| `reason`    | `str \| None`    | Why the file was partial, skipped or failed; `None` for `ok`.                  |
| `bytes_in`  | `int`            | The size of the original text, in bytes.                              |
| `bytes_out` | `int`            | The size of the text after the steps, in bytes.                       |

**Returns (from `extract`):** the reports are in `result.files`; you rarely build one yourself.

**Example usage:**

```python
from simplibs.extractor import extract

result = extract(source="my_project", profile="python/code-clean", dry_run=True)

[(f.relative, f.bytes_in, f.bytes_out) for f in result.ok_files]
# -> [('src/app.py', 62, 38), ('src/config.py', 10, 10)]       what the profile saved, file by file

for report in result.files:
    print(report.status, report.relative, report.reason)
```

The reasons a file is **not** `ok` (a `"partial"` file is in the output, the others are not):

| Status      | Reason                                                  | `bytes_in`        |
|-------------|---------------------------------------------------------|-------------------|
| `"partial"` | the text of the warning of the step (`not valid Python 3`) | the file's size |
| `"skipped"` | `not a text file`                                       | `0`               |
| `"skipped"` | `generated by simplibs-extractor`                       | the file's size   |
| `"skipped"` | `too large (1500000 > 1000000 bytes)`                   | the file's size   |
| `"error"`   | `read failed: …`                                        | `0`               |
| `"error"`   | `transform failed: …`                                   | the file's size   |

For a skipped or failed file `bytes_out` stays `0`. A problem of one file is **reported, never raised** — the
run goes on without it.

**`relative` next to `path`.** The report is read by people (relative, with the same separators on every
machine); the absolute path is for code that wants to open the file.

<details>
<summary>🔍 Under the hood</summary>

```python
@dataclass(frozen=True, slots=True)
class FileReport:
    path: Path
    relative: str
    status: FileStatus
    reason: str | None = None
    bytes_in: int = 0
    bytes_out: int = 0
```

The read phase creates the report; the loop body completes it:

```python
# read_source — the cheapest check first
return FileReport(path, relative, "skipped", "not a text file"), None
return FileReport(path, relative, "skipped", "generated by simplibs-extractor", size), None
return FileReport(path, relative, "skipped", f"too large ({size} > {max_size} bytes)", size), None
return FileReport(path, relative, "error", f"read failed: {describe_failure(exc)}"), None
return FileReport(path, relative, "ok", None, size), text
```

```python
# process_source — a step is somebody else's code, so its failure belongs to this one file
try:
    output = apply_steps(text, profile.steps, path.suffix)
except Exception as exc:
    failed = dataclasses.replace(report, status="error", reason=f"transform failed: {describe_failure(exc)}")
    return failed, None

done = dataclasses.replace(report, bytes_out=len(output.encode("utf-8")))
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `Entry`

**One file that is ready to be rendered** — exactly what a renderer receives, and nothing else.

**Attributes:**

| Name       | Type  | Description                                                    |
|------------|-------|----------------------------------------------------------------|
| `relative` | `str` | The path relative to the source, with `/` separators.          |
| `suffix`   | `str` | The lowercased suffix (`".py"`), or an empty string.           |
| `text`     | `str` | The text after the steps were applied.                         |

**Returns (from the transform phase):** a frozen `Entry` for every file with the status `ok`. You build one
yourself when you write or test a renderer.

**Example usage:**

```python
from simplibs.extractor import GENERATED_MARKER, Entry, register_renderer

def render_names(entries, context):                             # a renderer: entries in, text out
    names = "\n".join(entry.relative for entry in entries)
    return f"# {GENERATED_MARKER}\n{names}\n"

entries = [
    Entry("src/app.py", ".py", "print('hi')\n"),
    Entry("README.md", ".md", "# Demo\n"),
]
render_names(entries, None)                                     # -> '# simplibs-extractor:generated\nsrc/app.py\nREADME.md\n'

register_renderer("names", render_names)
```

**Why so little.** A renderer needs the path (for the header and the language), the suffix (for the code
fence) and the final text. It never sees the disk, the rules or the steps — which is why a renderer is easy to
test with a handful of hand-made entries.

The renderer contract — what else a renderer receives and what it must write — is described with
[the render phase](logic/README_EXTRACTOR_RENDER.md).

<details>
<summary>🔍 Under the hood</summary>

```python
@dataclass(frozen=True, slots=True)
class Entry:
    relative: str
    suffix: str
    text: str
```

The loop body creates it only for an included file:

```python
# process_source
# 3. Included: remember how large the text is after the steps
done = dataclasses.replace(report, bytes_out=len(output.encode("utf-8")))
return done, Entry(done.relative, path.suffix.lower(), output)
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `Resolved`

**A configuration with every default filled in** — the plan the later phases work from. An internal object:
it is not exported from the package root.

```python
from simplibs.extractor.definitions import Resolved
```

**Attributes:**

| Name      | Type               | Description                                                                 |
|-----------|--------------------|-----------------------------------------------------------------------------|
| `config`  | `ExtractionConfig` | The config with a **normalized** `source` and a **concrete** `target`.      |
| `profile` | `Profile`          | The profile object — never a key and never `None`.                          |
| `format`  | `str`              | The output format that will actually be used, and which has a renderer.     |

**Returns (from `resolve_config`):** a frozen `Resolved`.

**Example usage:**

```python
from simplibs.extractor import ExtractionConfig
from simplibs.extractor.logic import resolve_config

plan = resolve_config(ExtractionConfig(source="my_project"), {})

plan.profile.key                                        # -> 'generic/all'     None became the built-in profile
plan.format                                             # -> 'markdown'        None became the profile's format
plan.config.target.name                                 # -> 'extraction.md'   None became source / profile.output_name
plan.config.target.parent == plan.config.source         # -> True
```

**Why it exists.** Every later phase can rely on a normalized source, a concrete target, a real profile and a
known format, without repeating the `None` checks. Everything that can fail in the configuration fails **while
this object is being built** — before any file is touched.

<details>
<summary>🔍 Under the hood</summary>

```python
@dataclass(frozen=True, slots=True)
class Resolved:
    config: ExtractionConfig
    profile: Profile
    format: str
```

`resolve_config` fills it in (shortened):

```python
# 3. The source must be a real folder
source = normalize_path(config.source)
if not source.is_dir():
    raise_source_not_found_error(source)

# 4. The profile, and from it the default target and format
profile = resolve_profile(config.profile)
target = normalize_path(config.target) if config.target is not None else source / profile.output_name
output_format = config.format if config.format is not None else profile.format

# 5. The format must have a renderer (raises with the list of known formats)
get_renderer(output_format)

# 6. Everything is concrete from here on
resolved_config = dataclasses.replace(config, source=source, target=target)
return Resolved(resolved_config, profile, output_format)
```

</details>

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../README.md#-definitions--data-objects)
