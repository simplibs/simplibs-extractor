# 🔍 `logic/select` — Phase 1: Which Files

The first phase of an extraction answers two questions **before any file is opened**:

1. **What exactly will this run do?** — every default is filled in, and everything that can be refused is
   refused: a missing folder, an unknown profile, an unknown format, a mistyped parameter.
2. **Which files take part?** — the folder is scanned and the rules of the profile and of the config are
   applied.

```
ExtractionConfig + keywords ──► resolve_config ──► Resolved ──► select_sources ──► [paths]
                                  (defaults, checks)              (scan, rules)
```

The phase **never reads the content of a file**. Rules in this phase judge a path by its text (suffix, name,
folders); whatever needs the disk — whether a file is binary, how large it is — belongs to the
[read phase](README_EXTRACTOR_READ.md).

```python
from simplibs.extractor import ExtractionConfig
from simplibs.extractor.logic import resolve_config, select_sources
from simplibs.path.rules import HasSuffix

plan = resolve_config(ExtractionConfig(source="my_project", include=HasSuffix(".py")), {})
paths = select_sources(plan)
[path.relative_to(plan.config.source).as_posix() for path in paths]
# -> ['src/app.py', 'src/config.py', 'tests/test_app.py']
```

`extract()` calls these two functions first, in this order, and then goes on to the read phase with the list
of paths. A configuration that cannot run therefore fails in the first moments, not after a scan of the
whole project.

## What is public

The functions of this package are the machinery of `extract()`. They are importable from
`simplibs.extractor.logic` (`resolve_config`, `select_sources`; both in its `__all__`) and `simplibs.extractor.logic.select` (the
rest), but they are **not exported from the package root** — your programs call `extract()`, which is the
validated entry point. They are documented here for readers who want to know exactly what a run decides, for
tools built on top of the extractor and for tests.

| Function               | What it does                                                          | Used by           |
|------------------------|-----------------------------------------------------------------------|-------------------|
| `resolve_config`       | fills in the defaults and checks the configuration                    | `extract`         |
| `resolve_profile`      | turns a profile, a key or `None` into a profile object                | `resolve_config`, `generate_local_script` |
| `resolve_ignore_names` | the names the scan skips — the default or the chosen ones             | `select_sources`  |
| `select_sources`       | scans the folder and applies the rules                                | `extract`         |
| `all_of`               | combines rules with AND, ignoring `None`                              | `select_sources`  |
| `any_of`               | combines rules with OR, ignoring `None`                               | `select_sources`  |

---

## 🧭 Table of Contents

**Resolving the configuration**

* [`resolve_config`](#resolve_config)
* [`resolve_profile`](#resolve_profile)

**Choosing the files**

* [`select_sources`](#select_sources)
* [`resolve_ignore_names`](#resolve_ignore_names)
* [`all_of`](#all_of)
* [`any_of`](#any_of)

[⬅️ Back to main README](../../README.md#-the-six-phases)

---

### `resolve_config`

**Fills in every default and checks what can be checked before any file is read.** Turns *"what the caller
wrote"* into *"what the run will do"*.

**Parameters:**

| Name        | Type                      | Description                                                                    |
|-------------|---------------------------|--------------------------------------------------------------------------------|
| `config`    | `ExtractionConfig \| None`| A ready config, or `None` to build one from `overrides` alone.                 |
| `overrides` | `Mapping[str, Any]`       | Config fields to set (or to change in `config`) — the keywords of `extract()`. |

**Returns:** a [`Resolved`](../README_EXTRACTOR_DEFINITIONS.md#resolved) — a normalized source, a concrete
target, a profile object and a known format.

**Raises:**
`ParamError` (`EXTRACTOR_CONFIG_INVALID`) — a name in `overrides` is not a field of `ExtractionConfig`; there
is neither a config nor a `source`; the format has no registered renderer.
`NotFoundError` (`EXTRACTOR_SOURCE_NOT_FOUND`) — the source is not an existing directory.
`NotFoundError` (`EXTRACTOR_PROFILE_NOT_FOUND`) — a profile key is not registered.
`ValidationError` — a value in `overrides` has the wrong type (`overwrite="clobber"`).

**Example usage:**

```python
from simplibs.extractor import ExtractionConfig
from simplibs.extractor.logic import resolve_config

# 1. From a config alone
plan = resolve_config(ExtractionConfig(source="my_project"), {})
plan.profile.key                                        # -> 'generic/all'     None became the built-in profile
plan.format                                             # -> 'markdown'        None became the profile's format
plan.config.target.name                                 # -> 'extraction.md'   None became source / profile.output_name

# 2. From keywords alone
plan = resolve_config(None, {"source": "my_project", "profile": "generic/all", "add_tree": False})

# 3. A config changed by keywords — a copy, the original is untouched
config = ExtractionConfig(source="my_project")
plan = resolve_config(config, {"dry_run": True})
plan.config.dry_run                                     # -> True
config.dry_run                                          # -> False

# 4. Everything that can fail, fails here
resolve_config(None, {"sourse": "my_project"})          # raises ParamError — the card lists every valid name
resolve_config(None, {})                                # raises ParamError — no config and no source
resolve_config(None, {"source": "no_such_folder"})      # raises NotFoundError
resolve_config(None, {"source": "my_project", "profile": "python/nope"})   # raises NotFoundError
resolve_config(None, {"source": "my_project", "format": "html"})           # raises ParamError — no such renderer
```

**What it does, in order.**

| Step | What happens                                                                                              |
|-----:|-----------------------------------------------------------------------------------------------------------|
|  1   | Names that are not config fields are refused — a typo must not vanish into the keywords.                  |
|  2   | The config is built from the keywords, or the given config is changed with `dataclasses.replace`.         |
|  3   | The source is normalized and must be a directory.                                                         |
|  4   | The profile is resolved; from it come the default target (`source / profile.output_name`) and format.     |
|  5   | The format must have a renderer.                                                                          |
|  6   | A `Resolved` is returned with a concrete `source`, a concrete `target`, a real profile and a known format.|

**Why unknown names are checked by hand.** `extract(sourse=...)` must not disappear into `**overrides`. The
card lists the valid names, so the typo is fixed at a glance.

**Why everything fails early.** A wrong folder, an unknown profile or an unknown format cost nothing here;
found after a scan, they would have cost the whole scan.

**The target is never `None` afterwards.** It is `source / profile.output_name` unless you chose a path.

<details>
<summary>🔍 Under the hood</summary>

```python
def resolve_config(
    config: ExtractionConfig | None,
    overrides: Mapping[str, Any],
) -> Resolved:

    # 1. Reject names that are not config fields (a typo should not vanish)
    known = sorted(field.name for field in dataclasses.fields(ExtractionConfig))
    unknown = sorted(set(overrides) - set(known))
    if unknown:
        raise_unknown_parameter_error(unknown, known)

    # 2. Build or change the config
    if config is None:
        if "source" not in overrides:
            raise_missing_source_error()
        config = ExtractionConfig(**overrides)
    elif overrides:
        config = dataclasses.replace(config, **overrides)

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

### `resolve_profile`

**Turns a profile, a key or `None` into a profile object** — three ways to name a profile, one result.

**Parameters:**

| Name      | Type                       | Description                                                                         |
|-----------|----------------------------|-------------------------------------------------------------------------------------|
| `profile` | `Profile \| str \| None`   | A `Profile` (used as it is), a registered key, or `None` for the default.           |

**Returns:** the `Profile`.

**Raises:**
`NotFoundError` (`EXTRACTOR_PROFILE_NOT_FOUND`) — a key is not registered.

**Example usage:**

```python
from simplibs.extractor import Profile
from simplibs.extractor.logic.select import resolve_profile

resolve_profile(None).key                               # -> 'generic/all'          nothing chosen: the built-in profile
resolve_profile("generic/all").key                      # -> 'generic/all'          a key is looked up in the registry

one_off = Profile(system="demo", name="one-off")
resolve_profile(one_off) is one_off                     # -> True                   a ready object is used as it is, registered or not

resolve_profile("python/nope")                          # raises NotFoundError — the card lists the registered keys
```

**Why a profile object is accepted.** `ExtractionConfig.profile` takes a ready object for a **one-off
profile that is never registered**, a key for the everyday case, and nothing for the default. All three end
here as the same thing.

<details>
<summary>🔍 Under the hood</summary>

```python
def resolve_profile(profile: Profile | str | None) -> Profile:

    # 1. Nothing chosen: the built-in profile
    if profile is None:
        return get_profile(DEFAULT_PROFILE_KEY)

    # 2. Already a profile
    if isinstance(profile, Profile):
        return profile

    # 3. A key
    return get_profile(profile)
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `select_sources`

**Collects the files an extraction takes** — scans the folder, drops the output and the skipped files, applies
the `include` and `exclude` rules.

**Parameters:**

| Name   | Type       | Description                      |
|--------|------------|----------------------------------|
| `plan` | `Resolved` | The resolved configuration.      |

**Returns:** a `list[Path]` — the **absolute** paths of the selected files, sorted.

**Example usage:**

```python
from simplibs.extractor import ExtractionConfig
from simplibs.extractor.logic import resolve_config, select_sources
from simplibs.path.rules import HasSuffix, ParentNameIs

def names(plan):
    return [path.relative_to(plan.config.source).as_posix() for path in select_sources(plan)]

# my_project/
#   README.md   logo.png   src/app.py   src/config.py   tests/test_app.py

plan = resolve_config(ExtractionConfig(source="my_project", include=HasSuffix(".py")), {})
names(plan)                                             # -> ['src/app.py', 'src/config.py', 'tests/test_app.py']

plan = resolve_config(ExtractionConfig(
    source="my_project",
    include=HasSuffix(".py"),
    exclude=ParentNameIs("tests"),                      # a file directly in a folder named tests
), {})
names(plan)                                             # -> ['src/app.py', 'src/config.py']

plan = resolve_config(ExtractionConfig(source="my_project", recursive=False, include=HasSuffix(".md")), {})
names(plan)                                             # -> ['README.md']       sub-folders are not scanned
```

**The profile and the config are combined, and the config can only narrow.**

| Rule      | Combined by | Meaning                                                                     |
|-----------|-------------|-----------------------------------------------------------------------------|
| `include` | **AND**     | a file must pass the profile's `include` **and** the config's `include`     |
| `exclude` | **OR**      | a file is dropped if the profile excludes it **or** the config does         |

A config therefore never brings back a file the profile has already left out.

**What is removed before the rules are applied.**

* the **output itself** (`config.target`) — an extraction is never its own input;
* everything in **`skip_paths`** — for example an embedded script;
* the names of the **ignore set** (`ignore_names`; see [`resolve_ignore_names`](#resolve_ignore_names)).

Outputs of an **earlier** run under other names (`extraction (1).md`, a backup) are not caught here — the
[read phase](README_EXTRACTOR_READ.md) recognizes them by their marker.

**The rules see the relative path.** With an absolute path, a rule such as *"a parent folder is named
`tests`"* would drop a whole project that merely lies inside a folder called `tests`. On the path relative to
the source, only the project's own folders count — and it does not matter where on the disk the project
lies.

**A binary file is selected, too.** `logo.png` passes `generic/all` — this phase only judges names. The read
phase drops it, with the reason `not a text file`.

<details>
<summary>🔍 Under the hood</summary>

```python
def select_sources(plan: Resolved) -> list[Path]:
    config, profile = plan.config, plan.profile

    # 1. One rule each: the config can only narrow the profile
    include = all_of(profile.include, config.include)
    exclude = any_of(profile.exclude, config.exclude)

    # 2. Scan the folder (only collecting; the rules are applied below)
    files = collect_files(
        config.source,
        recursive=config.recursive,
        ignore_names=resolve_ignore_names(config.ignore_names),
    )

    # 3. Never read the output itself or anything the caller asked to skip
    banned = {config.target, *(normalize_path(path) for path in config.skip_paths)}

    # 4. Apply the rules to the relative path
    selected: list[Path] = []
    for file in files:
        if normalize_path(file) in banned:
            continue
        relative = relativize_path(file, config.source)
        if include is not None and not include(relative):
            continue
        if exclude is not None and exclude(relative):
            continue
        selected.append(file)

    return selected
```

The scan only **collects**. The `include_filter` and `exclude_filter` of `collect_files` are not used, because
they would see absolute paths.

</details>

[▲ Back to top](#-table-of-contents)

---

### `resolve_ignore_names`

**Returns the names the scan skips** — a folder or a file name that is never looked at.

**Parameters:**

| Name           | Type                    | Description                                    |
|----------------|-------------------------|------------------------------------------------|
| `ignore_names` | `frozenset[str] \| None`| The names chosen in the config, or `None`.     |

**Returns:** a `frozenset[str]` — the chosen names **as they are**, or, for `None`, the default set: the
`DEFAULT_IGNORE_NAMES` of `simplibs-path` **plus** the draft files of `SafeFileWriter`
(`IGNORE_DRAFTS`).

**Example usage:**

```python
from simplibs.file import IGNORE_DRAFTS
from simplibs.path import DEFAULT_IGNORE_NAMES, IGNORE_GENERIC
from simplibs.extractor import ExtractionConfig
from simplibs.extractor.logic.select import resolve_ignore_names

resolve_ignore_names(None) == DEFAULT_IGNORE_NAMES | IGNORE_DRAFTS      # -> True     the default
resolve_ignore_names(frozenset({"vendor"}))                             # -> frozenset({'vendor'})    a choice REPLACES the default

# the default plus something of your own — you write the union yourself:
ExtractionConfig(source="my_project", ignore_names=DEFAULT_IGNORE_NAMES | IGNORE_DRAFTS | {"vendor"})

# also skip ambiguous folders such as build, dist or site (they are opt-in):
ExtractionConfig(source="my_project", ignore_names=DEFAULT_IGNORE_NAMES | IGNORE_DRAFTS | IGNORE_GENERIC)
```

**What the default skips.** Version-control metadata (`.git`), virtual environments, installed dependencies
(`node_modules`), caches (`__pycache__`), editor settings and OS housekeeping files. Ambiguous names such as
`build` or `dist` are **not** in the default, because they are also ordinary folder names — add
`IGNORE_GENERIC` when you want them skipped.

**A choice replaces, it does not extend.** `ignore_names=frozenset({"vendor"})` means exactly that, and
nothing else. Anyone who wants the default plus something writes the union themselves — the same rule
`simplibs-path` follows. A set you give should therefore include `IGNORE_DRAFTS` too, or the half-written
draft file of a crashed write could be picked up by the next run.

**Why the drafts are in the default.** The extractor writes its output with `SafeFileWriter`, which leaves a
draft file for the moment of the write (or for good after a crash). `simplibs-path` does not know about it, so
the default has to add it.

<details>
<summary>🔍 Under the hood</summary>

```python
def resolve_ignore_names(ignore_names: frozenset[str] | None) -> frozenset[str]:

    # 1. A choice replaces the default completely
    if ignore_names is not None:
        return ignore_names

    # 2. Default: the usual housekeeping folders and half-written drafts
    return DEFAULT_IGNORE_NAMES | IGNORE_DRAFTS
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `all_of`

**Combines rules with AND**, ignoring the ones that are `None`.

**Parameters:**

| Name     | Type            | Description                                             |
|----------|-----------------|---------------------------------------------------------|
| `*rules` | `Rule \| None`  | The rules; `None` means *"no rule here"*.               |

**Returns:** one `Rule` that needs **every** given rule to pass; `None` if no rule was given.

**Example usage:**

```python
from pathlib import Path
from simplibs.extractor.logic.select import all_of
from simplibs.path.rules import HasSuffix, ParentNameIs

rule = all_of(HasSuffix(".py"), None, ~ParentNameIs("tests"))   # the None is dropped

rule(Path("src/app.py"))                                # -> True
rule(Path("tests/test_app.py"))                         # -> False      not allowed in tests
rule(Path("README.md"))                                 # -> False      not a .py file

all_of(None, None)                                      # -> None       nothing to combine: no constraint
all_of(HasSuffix(".py"))                                # the rule itself
```

**Why `None` is dropped.** A profile and a config each may or may not have an `include` rule. For AND an
absent rule changes nothing, so it is left out of the fold, and the scan asks **a single question**.

<details>
<summary>🔍 Under the hood</summary>

```python
def all_of(*rules: Rule | None) -> Rule | None:

    # 1. Keep only real rules
    present = [rule for rule in rules if rule is not None]

    # 2. Fold with `&`, or return None when there is nothing to combine
    return functools.reduce(operator.and_, present) if present else None
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `any_of`

**Combines rules with OR**, ignoring the ones that are `None`.

**Parameters:**

| Name     | Type            | Description                                             |
|----------|-----------------|---------------------------------------------------------|
| `*rules` | `Rule \| None`  | The rules; `None` means *"no rule here"*.               |

**Returns:** one `Rule` that passes when **any** given rule passes; `None` if no rule was given.

**Example usage:**

```python
from pathlib import Path
from simplibs.extractor.logic.select import any_of
from simplibs.path.rules import HasSuffix, ParentNameIs

rule = any_of(ParentNameIs("tests"), None, HasSuffix(".log"))

rule(Path("tests/test_app.py"))                         # -> True       excluded by the first rule
rule(Path("run.log"))                                   # -> True       excluded by the third
rule(Path("src/app.py"))                                # -> False      nothing excludes it

any_of(None, None)                                      # -> None       nothing excludes anything
```

**Why `None` is dropped.** Exclusions add up: a file is dropped if the profile excludes it **or** the config
does. An absent exclusion excludes nothing, so it is left out of the fold.

<details>
<summary>🔍 Under the hood</summary>

```python
def any_of(*rules: Rule | None) -> Rule | None:

    # 1. Keep only real rules
    present = [rule for rule in rules if rule is not None]

    # 2. Fold with `|`, or return None when there is nothing to combine
    return functools.reduce(operator.or_, present) if present else None
```

</details>

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../../README.md#-the-six-phases)
