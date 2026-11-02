# 🏷️ `annotations` — Shared Annotations

The `annotations` package holds the types the whole library shares — the exact types the
configuration, the profile, the report and the functions declare for their fields and parameters. They are
exported from the package root, so **your own code can accept exactly what this library accepts**:

```python
from simplibs.extractor import FileStatus, OutputFormat, OverwritePolicy, StepsSpec
```

Each is a plain annotation object — no class to instantiate — and works with `simplibs-validate`
(`@validate_call`, `@validate_dataclass`) and with type checkers.

```python
from simplibs.validate import validate_call
from simplibs.extractor import OutputFormat, OverwritePolicy

@validate_call
def export(name: OutputFormat, policy: OverwritePolicy = "overwrite") -> None: ...

export("markdown")                      # fine
export("Markdown")                      # raises ValidationError — a format name is lowercase
export("markdown", policy="clobber")    # raises ValidationError — not one of the four policies
```

The same annotations are what `ExtractionConfig` and `Profile` use for their fields, so a mistake is
caught **when the object is built** — before any file is read or written.

## Three kinds of annotation

| Kind                | Annotations                          | How it decides                                                                                      |
|---------------------|--------------------------------------|-----------------------------------------------------------------------------------------------------|
| **Fixed set**       | `FileStatus`, `OverwritePolicy`      | A `Literal` — only the listed values exist.                                                          |
| **Annotated type**  | `OutputFormat`                       | `Annotated[str, predicate]` — a base type plus a predicate that checks the **shape** of the value.   |
| **Type alias**      | `StepsSpec`                          | A union of existing types — one `Action`, a mapping `suffix -> Action`, or `None`.                  |

A fixed set fails at the signature on a typo (`overwrite="overwite"`) instead of months later, when the
run meets an existing output. To an editor an annotated type is its plain base type, while
`@validate_call` reads the predicate from the metadata and checks the value.

`PathLike` and `ByteCount` are **not** redefined here — they come from `simplibs-path` and
`simplibs-file`, and `ExtractionConfig` uses them as they are.

## Where each one is used

| Annotation        | Where                                                     | Used by                                                                          |
|-------------------|-----------------------------------------------------------|----------------------------------------------------------------------------------|
| `FileStatus`      | `FileReport.status`                                       | the read and transform phases (they decide it), the summary, the exit code       |
| `OutputFormat`    | `Profile.format`, `ExtractionConfig.format`, `register_renderer(name)` | the registry, `resolve_config`                                       |
| `OverwritePolicy` | `ExtractionConfig.overwrite`, `write_output(policy)`      | the write phase; the command's `--overwrite` choices are taken from it           |
| `StepsSpec`       | `Profile.steps`                                           | `steps_for`, `apply_steps` (the transform phase)                                 |

> **Shape here, existence elsewhere.** An annotation only says whether a value has the right
> *form*. Whether a renderer with the name `"html"` exists is known to the registry, a layer further
> to the right, and is checked when the configuration is resolved — see
> [`OutputFormat`](#outputformat).

---

## 🧭 Table of Contents

**Fixed sets**

* [`FileStatus`](#filestatus)
* [`OverwritePolicy`](#overwritepolicy)

**Annotated types**

* [`OutputFormat`](#outputformat)

**Type aliases**

* [`StepsSpec`](#stepsspec)

[⬅️ Back to main README](../README.md#-annotations-and-constants)

---

### `FileStatus`

The **outcome of one file** — it entered the output whole, it entered the output but was not fully processed, it was left out on purpose, or it failed.

**Definition:**

```python
FileStatus = Literal["ok", "partial", "skipped", "error"]
```

**Accepts:** `"ok"`, `"partial"`, `"skipped"`, `"error"`.

**Rejects:** anything else (`"failed"`, `"OK"`, `None`) — wherever a validated function or dataclass
declares it. The library itself only ever sets one of the four values.

| Value       | Meaning                                                                      | Examples                                                          |
|-------------|------------------------------------------------------------------------------|-------------------------------------------------------------------|
| `"ok"`      | The file entered the output.                                                 | a Python source, a README                                         |
| `"partial"` | The file entered the output, but a step could not process it fully — it **warned**. | a Python source that does not parse: it is in the output as the steps left it |
| `"skipped"` | The file was left out **on purpose** — nothing is wrong.                     | a binary file, a file larger than the limit, an earlier output of this library |
| `"error"`   | The file failed; the run **continued** without it.                           | a read that failed, a step that raised or returned something but text |

**Example usage:**

```python
from simplibs.extractor import extract

result = extract(source="my_project", dry_run=True)

[f.relative for f in result.ok_files]                   # -> ['README.md', 'src/app.py']
[(f.relative, f.reason) for f in result.skipped_files]  # -> [('logo.png', 'not a text file')]
result.error_files                                      # -> ()
result.success                                          # -> True
```

**Why four values and not two.** A `partial` file is in the output, so it fails nothing either. `skipped` is not a failure and `error` is not a stop. Keeping the two
apart is what lets the report and the exit code tell *"nothing is wrong"* from *"something needs a
look"*: a skipped file never changes the verdict, a failed file makes `success` false.

<details>
<summary>🔍 Under the hood</summary>

```python
FileStatus = Literal["ok", "partial", "skipped", "error"]
"""The outcome of one file: included whole, included but not fully processed, left out on purpose, or failed."""
```

`ExtractionResult` filters its reports by this value:

```python
@property
def ok_files(self) -> tuple[FileReport, ...]:
    return tuple(report for report in self.files if report.status == "ok")

@property
def success(self) -> bool:
    return self.fatal is None and not self.error_files and bool(self.ok_files or self.partial_files)
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `OverwritePolicy`

What happens **when the output file already exists**.

**Definition:**

```python
OverwritePolicy = Literal["overwrite", "unique", "backup", "error"]
```

**Accepts:** `"overwrite"`, `"unique"`, `"backup"`, `"error"`.

**Rejects:** anything else (`"replace"`, `"Overwrite"`, `True`, `None`).

| Value         | If the output exists                                                              | Default |
|---------------|-----------------------------------------------------------------------------------|:-------:|
| `"overwrite"` | replaces it **atomically** (a draft is written first, then swapped in)            |   ✅    |
| `"unique"`    | writes a numbered copy next to it (`extraction (1).md`) and leaves the old file   |         |
| `"backup"`    | keeps the old file as a backup, then replaces it                                  |         |
| `"error"`     | refuses to write — `EXTRACTOR_TARGET_EXISTS`, **also in a dry run**               |         |

If the output does not exist yet, all four simply write it.

**Example usage:**

```python
from simplibs.extractor import ExtractionConfig, extract

extract(source="my_project")                                    # my_project/extraction.md, replaced on every run
extract(source="my_project", overwrite="unique")                # my_project/extraction (1).md next to the old one
extract(source="my_project", overwrite="backup")                # the old output survives as a backup file
extract(source="my_project", overwrite="error")                 # raises AlreadyExistsError if the output exists

ExtractionConfig(source="my_project", overwrite="clobber")      # raises ValidationError — not one of the four
```

On the command line the same four words are the choices of `--overwrite`; the list is read from this
annotation, so a policy added here appears in the command's help by itself.

**Why `"overwrite"` is the default.** An extractor is re-run constantly and its output is generated,
never hand-edited. The replacement itself is atomic, so a run that stops halfway leaves the previous
output intact.

**Why `"error"` fails in a dry run too.** A dry run reports what the real run *would* do. If it
passed and the real run then refused, it would promise a write that never happens.

Details of the decision — the order of the checks, the numbered name, the backup — are in
[`write_output`](logic/README_EXTRACTOR_WRITE.md).

<details>
<summary>🔍 Under the hood</summary>

```python
OverwritePolicy = Literal["overwrite", "unique", "backup", "error"]
"""What happens when the output file already exists."""
```

The write phase is the only place that reads it:

```python
# 2. The `error` policy fails before anything else, also in a dry run
exists = target.exists()
if exists and policy == "error":
    raise_target_exists_error(target)

# 3. `unique` writes next to the existing file under a numbered name
final = make_unique_path(target) if exists and policy == "unique" else target

# 5. `backup` keeps the old file before it is replaced
if exists and policy == "backup":
    backup_file(target)
```

The command line builds its choices from the same annotation:

```python
parser.add_argument("--overwrite", choices=get_args(OverwritePolicy), default="overwrite", ...)
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `OutputFormat`

The **name of an output format** — `"markdown"`, `"plain"`, or a format you registered.

**Definition:**

```python
OutputFormat = Annotated[str, is_output_format]
```

**Accepts:** a lowercase name that starts with a letter and continues with letters, digits, `_` or `-` —
`"markdown"`, `"plain"`, `"json-manifest"`, `"my_format"`, `"v2"`.

**Rejects:** `"Markdown"` (uppercase), `""`, `"md file"` (a space), `"2md"` (starts with a digit),
`"a/b"` (a path separator), non-strings.

**Example usage:**

```python
from simplibs.extractor import ExtractionConfig, extract, register_renderer

ExtractionConfig(source="my_project", format="plain")           # fine
ExtractionConfig(source="my_project", format="Markdown")        # raises ValidationError — wrong shape

register_renderer("Names", lambda entries, context: "")         # raises ValidationError — wrong shape

extract(source="my_project", format="html")                     # raises ParamError — right shape,
                                                                #   but no renderer is registered as "html"
```

Two different failures, two different layers: a name of the **wrong form** is stopped by the
annotation when the object is built; a name of the right form that **nobody registered** is stopped
when the configuration is resolved, and the card lists the formats that exist.

**Why a name and not a closed list.** Renderers are registered by name, so the set of formats is open.
A `Literal["markdown", "plain"]` would freeze it at the two built-in formats and turn every added
renderer into a typing error.

**Why `Annotated`.** An editor sees a plain `str`; `@validate_call` and `@validate_dataclass` read the
predicate from the metadata and reject a malformed name at the signature.

<details>
<summary>🔍 Under the hood</summary>

```python
OutputFormat = Annotated[str, is_output_format]
```

The predicate — private, not exported:

```python
_FORMAT_NAME = re.compile(r"[a-z][a-z0-9_-]*")

def is_output_format(name: str) -> bool:
    # 1. Only a string can name a format
    if not isinstance(name, str):
        return False

    # 2. Lowercase word characters only — no spaces, no path separators
    return _FORMAT_NAME.fullmatch(name) is not None
```

It checks the **shape**, never the existence: the registry is a layer further to the right, so the
existence check lives in `resolve_config`:

```python
# 5. The format must have a renderer (raises with the list of known formats)
get_renderer(output_format)
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `StepsSpec`

**How a profile transforms the text of its files** — nothing, one pipeline for everything, or one
pipeline per suffix.

**Definition:**

```python
StepsSpec: TypeAlias = Action | Mapping[str, Action] | None
```

| Shape                    | Meaning                                                                 |
|--------------------------|-------------------------------------------------------------------------|
| `None`                   | The text stays as it is.                                                |
| one `Action`             | The action is applied to **every** file.                                |
| `{".py": action, ...}`   | The action of the file's own suffix is applied; the key `"*"` is the **fallback** for every other file. A file with no matching key and no `"*"` is left unchanged. |

**Rules for the mapping keys:** `"*"`, or a **lowercase** suffix that starts with a dot and has at least
one more character (`".py"`, `".md"`). `"py"` and `".PY"` can never match a file and are refused when the
profile is built (`EXTRACTOR_PROFILE_INVALID`).

**Example usage:**

```python
import re
from simplibs.extractor import Profile
from simplibs.text.actions import RemoveMatches
from simplibs.text.presets import COMPACT

strip_comments = RemoveMatches(pattern=re.compile(r"#.*"))

Profile(system="demo", name="none")                                        # steps=None: every file unchanged
Profile(system="demo", name="one", steps=strip_comments >> COMPACT)        # one Action for every file
Profile(
    system="demo", name="per-suffix",
    steps={".py": strip_comments >> COMPACT, "*": COMPACT},                # .py cleaned harder, the rest only compacted
)

Profile(system="demo", name="bad", steps={"py": COMPACT})                  # raises ParamError — "py" can never match
```

**Why a mapping exists.** A step receives **only the text**, never the path, so it cannot know which
language it is cleaning. A profile that cleans Python and JavaScript differently therefore needs the
choice made *before* the step runs — which is what the mapping does.

**Why not always a mapping.** Most profiles apply one action to everything; forcing `{"*": action}` on
them would be noise.

> **The action comes from [`simplibs-actions`](https://pypi.org/project/simplibs-actions/).** The text
> actions above are from [`simplibs-text`](https://pypi.org/project/simplibs-text/), which is not a
> dependency of the extractor — install it when you want those steps. Any `Action` works.

The three shapes are understood in exactly one place, [`steps_for`](logic/README_EXTRACTOR_TRANSFORM.md).

<details>
<summary>🔍 Under the hood</summary>

```python
StepsSpec: TypeAlias = Action | Mapping[str, Action] | None
```

`steps_for` is the one place that understands the three shapes:

```python
def steps_for(steps: StepsSpec, suffix: str) -> Action | None:
    # 1. No steps at all
    if steps is None:
        return None

    # 2. A mapping: the file's own suffix, otherwise the fallback "*"
    if isinstance(steps, Mapping):
        return steps.get(suffix.lower(), steps.get("*"))

    # 3. One action for every file
    return steps
```

The suffix of the file is lowercased for the lookup — that is why the keys of the mapping must be
lowercase.

The keys are checked in `Profile.__post_init__`:

```python
if isinstance(self.steps, Mapping):
    for suffix in self.steps:
        if not is_suffix_key(suffix):
            raise_profile_steps_key_error(suffix)
```

</details>

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../README.md#-annotations-and-constants)
