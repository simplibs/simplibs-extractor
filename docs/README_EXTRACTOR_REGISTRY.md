# 🧩 `registry` — Profiles and Renderers by Name

The `registry` package is where the extractor keeps **what can be chosen by name**: the **profiles**
(`"python/code-clean"`) and the **output formats** (`"markdown"`). Everything that is chosen by a word — the
`profile=` of a run, the `--format` of the command, the keys typed on a command line — is looked up here.

There are **two registries**, each a module-level dictionary shared by the whole process:

| Registry          | Key                                  | Value                       | Written by                         | Read by                                              |
|-------------------|--------------------------------------|-----------------------------|------------------------------------|------------------------------------------------------|
| **Profiles**      | `"system/name"` (`"python/code-clean"`) | a `Profile`              | `register_profile` (add-ons, you)  | `get_profile`, `list_profiles`, `list_systems`, every run |
| **Renderers**     | the format name (`"markdown"`)       | a function `(entries, context) -> str` | `register_renderer` (the library, add-ons, you) | `get_renderer`, `list_formats`, every run |

```python
from simplibs.extractor import get_profile, list_formats, list_systems

list_systems()                          # -> ['generic']
list_formats()                          # -> ['markdown', 'plain']
get_profile("generic/all").description  # -> 'Every text file, unchanged.'
```

Two things exist **as soon as the package is imported**: the profile `generic/all` and the formats
`markdown` and `plain`. That is why the extractor is useful without any add-on. Nothing else is registered
until you — or an add-on — register it.

## The dictionaries are private

The two dictionaries themselves (`PROFILE_REGISTRY`, `RENDERER_REGISTRY`) are a private detail. You always go
through the functions: they validate what goes in, give a helpful card for what is missing, and hand out
**copies** (`list_profiles` returns a new list), so the registry cannot be changed by accident through a
result.

There is exactly one registry per process, and add-ons register into it when they are loaded. A class would
only add an instance nobody else may create — which is why it is a dictionary.

## Add-ons are not loaded by themselves

An installed add-on registers its profiles only when it is **asked** to. The command line does that for you
before it builds its parser; in Python you call [`load_plugins()`](README_EXTRACTOR_PLUGINS.md) once:

```python
from simplibs.extractor import list_systems, load_plugins

list_systems()                          # -> ['generic']
loaded, failed = load_plugins()         # every installed add-on registers its profiles
list_systems()                          # -> ['generic', 'python', 'react']      with simplibs-code-extractor installed
```

## Replace, but ask for it

Both `register_*` functions refuse a name that is taken, unless `replace_existing=True`. Two add-ons that
registered the same key would otherwise decide by import order; replacing is possible, but it has to be
**intended**. The library's own built-ins register with `replace_existing=True`, so re-importing or reloading
the package never fails on them.

## Functions

| Function              | Registry  | What it does                                                         |
|-----------------------|-----------|----------------------------------------------------------------------|
| `register_profile`    | profiles  | adds a profile under its key                                         |
| `get_profile`         | profiles  | returns the profile of a key, or a card that lists the registered ones |
| `list_profiles`       | profiles  | the registered profiles, sorted by key, optionally of one system     |
| `list_systems`        | profiles  | the systems that have at least one profile                           |
| `expand_profile_keys` | profiles  | turns typed names into full keys                                     |
| `register_renderer`   | renderers | adds a format                                                        |
| `get_renderer`        | renderers | returns the renderer of a format — and is the check that a format exists |
| `list_formats`        | renderers | the registered formats, sorted                                       |

---

## 🧭 Table of Contents

**Profiles**

* [`register_profile`](#register_profile)
* [`get_profile`](#get_profile)
* [`list_profiles`](#list_profiles)
* [`list_systems`](#list_systems)
* [`expand_profile_keys`](#expand_profile_keys)
* [`generic/all`](#genericall)

**Output formats**

* [`register_renderer`](#register_renderer)
* [`get_renderer`](#get_renderer)
* [`list_formats`](#list_formats)

[⬅️ Back to main README](../README.md#-profiles-registry-and-add-ons)

---

### `register_profile`

**Adds a profile to the registry** under its key.

**Parameters:**

| Name               | Type      | Default | Description                                                    |
|--------------------|-----------|---------|----------------------------------------------------------------|
| `profile`          | `Profile` |         | The profile to register.                                       |
| `replace_existing` | `bool`    | `False` | Allow replacing a profile that already has this key. *(keyword-only)* |

**Returns:** the registered `Profile`, so the call can be used as an expression.

**Raises:**
`AlreadyExistsError` (`EXTRACTOR_PROFILE_EXISTS`) — the key is taken and `replace_existing` is `False`.
`ValidationError` — `profile` is not a `Profile`.

**Example usage:**

```python
from simplibs.extractor import Profile, extract, register_profile
from simplibs.path.rules import HasSuffix

profile = register_profile(Profile(system="demo", name="python-only", include=HasSuffix(".py")))

profile.key                                             # -> 'demo/python-only'
extract(source="my_project", profile="demo/python-only")      # now it can be chosen by its key

register_profile(profile)                               # raises AlreadyExistsError — the key is taken
register_profile(profile, replace_existing=True)        # fine — replacing was asked for
```

**Why `Profile` objects only.** The profile checked itself when it was built (see
[`Profile`](README_EXTRACTOR_DEFINITIONS.md#profile)), so the registry never holds one that can not work.

**Why no silent replacement.** The key is the profile's identity. Replacing it behind a caller's back would
change what `profile="demo/python-only"` means everywhere in the process.

<details>
<summary>🔍 Under the hood</summary>

```python
@validate_call
def register_profile(
    profile: Profile,
    *,
    replace_existing: bool = False,
) -> Profile:
    # 1. Refuse a taken key unless replacing was asked for
    if profile.key in PROFILE_REGISTRY and not replace_existing:
        raise_profile_exists_error(profile.key)

    # 2. Store and hand back
    PROFILE_REGISTRY[profile.key] = profile
    return profile
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `get_profile`

**Returns the profile registered under a key** — and, when there is none, says what *is* registered.

**Parameters:**

| Name  | Type  | Description                                      |
|-------|-------|--------------------------------------------------|
| `key` | `str` | The full key (`"python/code-clean"`).            |

**Returns:** the registered `Profile`.

**Raises:**
`NotFoundError` (`EXTRACTOR_PROFILE_NOT_FOUND`) — no profile has this key; the card lists the registered keys.

**Example usage:**

```python
from simplibs.extractor import get_profile

profile = get_profile("generic/all")
profile.system, profile.name                            # -> ('generic', 'all')
profile.output_name                                     # -> 'extraction.md'

get_profile("python/code-claen")                        # raises NotFoundError — the card lists the registered keys
```

**Why the list.** A mistyped key is the most common profile error, and a list of what exists turns it into a
one-glance fix. The card has a second hint for the other usual cause: the profiles of an add-on exist only
**after the add-on has been loaded**.

<details>
<summary>🔍 Under the hood</summary>

```python
@validate_call
def get_profile(key: str) -> Profile:
    # 1. Look the key up
    profile = PROFILE_REGISTRY.get(key)

    # 2. Unknown key: say what exists
    if profile is None:
        raise_profile_not_found_error(key, sorted(PROFILE_REGISTRY))

    # 3. Found
    return profile
```

It is the only reader of a single profile: a run that is given a key (`extract(profile="…")`) ends up here
through `resolve_profile`.

</details>

[▲ Back to top](#-table-of-contents)

---

### `list_profiles`

**Lists the registered profiles**, sorted by key — all of them, or those of one system.

**Parameters:**

| Name     | Type          | Default | Description                                              |
|----------|---------------|---------|----------------------------------------------------------|
| `system` | `str \| None` | `None`  | Only the profiles of this system; `None` lists all.      |

**Returns:** a **new** `list[Profile]`; changing it does not touch the registry.

**Example usage:**

```python
from simplibs.extractor import list_profiles

[profile.key for profile in list_profiles()]            # -> ['generic/all']      without add-ons
[profile.key for profile in list_profiles("python")]    # -> []                   no such system: an empty list, not an error

for profile in list_profiles("generic"):
    print(profile.key, "-", profile.description)        # generic/all - Every text file, unchanged.
```

A system with no profiles is **not an error here** — it is an empty list. The command line is the one that
turns an unknown system into a refusal, because there a person typed it.

**Why sorted and detached.** It feeds `--list-profiles`, the interactive choice and tests, all of which want
a stable order. The result is a copy, so the registry cannot be changed through it.

<details>
<summary>🔍 Under the hood</summary>

```python
@validate_call
def list_profiles(system: str | None = None) -> list[Profile]:
    # 1. Sort by key so listings are stable
    profiles = sorted(PROFILE_REGISTRY.values(), key=lambda profile: profile.key)

    # 2. Narrow to one system if asked
    return [profile for profile in profiles if system is None or profile.system == system]
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `list_systems`

**Lists the systems** that have at least one registered profile, sorted.

**Parameters:** none.

**Returns:** a `list[str]`.

**Example usage:**

```python
from simplibs.extractor import Profile, list_systems, register_profile

list_systems()                                          # -> ['generic']

register_profile(Profile(system="demo", name="all"))
list_systems()                                          # -> ['demo', 'generic']
```

**A system is not registered on its own.** There is no `register_system`: a system exists **while a profile
names it**. It feeds `--list-systems` and the first question of the interactive prompt.

<details>
<summary>🔍 Under the hood</summary>

```python
@validate_call
def list_systems() -> list[str]:
    # 1. Each profile names its system; a set removes the repeats
    return sorted({profile.system for profile in PROFILE_REGISTRY.values()})
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `expand_profile_keys`

**Turns what a person typed into full profile keys.** The single place where `"python a,b"` becomes registry
keys, so the command line and the Python API agree.

**Parameters:**

| Name     | Type                   | Description                                                                                       |
|----------|------------------------|---------------------------------------------------------------------------------------------------|
| `system` | `str \| None`          | The default system for names without one; `None` if there is none.                                |
| `names`  | `str \| Sequence[str]` | One text with names separated by commas (`"a,b"`), or a sequence of names.                        |

**Returns:** a `list[str]` of full keys, in the order given.

**Raises:**
`ParamError` (`EXTRACTOR_PROFILE_INVALID`) — a name has no system and none was given, or no name was given at all.

**Example usage:**

```python
from simplibs.extractor import expand_profile_keys

expand_profile_keys("python", "code-clean,data-all")        # -> ['python/code-clean', 'python/data-all']
expand_profile_keys("python", "code-clean, data-all")       # -> ['python/code-clean', 'python/data-all']   spaces are trimmed
expand_profile_keys("python", ["code-clean", "data-all"])   # -> ['python/code-clean', 'python/data-all']   a sequence works too
expand_profile_keys("python", "code-clean,generic/all")     # -> ['python/code-clean', 'generic/all']       a full key is kept as it is
expand_profile_keys(None, "generic/all")                    # -> ['generic/all']

expand_profile_keys(None, "code-clean")                     # raises ParamError — 'code-clean' has no system
expand_profile_keys("python", " , ")                        # raises ParamError — no profile was given
```

**Full keys win.** A name that already contains `/` stays as it is even when a default system is given, so
one run can mix systems.

**It builds keys; it does not look them up.** Whether the keys are registered is decided later, by
[`get_profile`](#get_profile) — a mistyped name here becomes a `NotFoundError` there, with the list of what
exists.

<details>
<summary>🔍 Under the hood</summary>

```python
@validate_call
def expand_profile_keys(
    system: str | None,
    names: str | Sequence[str],
) -> list[str]:
    # 1. One text and a sequence are handled alike: split every item on commas
    items = [names] if isinstance(names, str) else list(names)
    parts = [part.strip() for item in items for part in item.split(",")]

    # 2. Build the keys
    keys: list[str] = []
    for part in parts:
        if not part:
            continue
        if "/" in part:
            keys.append(part)
        elif system:
            keys.append(f"{system}/{part}")
        else:
            raise_missing_system_error(part)

    # 3. Nothing usable was given
    if not keys:
        raise_no_profile_given_error(names)

    return keys
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `generic/all`

**The built-in profile** — every text file, unchanged. It needs no add-on and is what a run uses when no
profile is chosen.

| Field         | Value                          |
|---------------|--------------------------------|
| `system`      | `"generic"`                    |
| `name`        | `"all"`                        |
| `description` | `"Every text file, unchanged."`|
| `include`     | `None` — no rule of its own    |
| `exclude`     | `None`                         |
| `steps`       | `None` — the text is not changed |
| `output_name` | `"extraction.md"`              |
| `format`      | `"markdown"`                   |

Its key is the constant `DEFAULT_PROFILE_KEY`. The profile object is internal (`GENERIC_ALL`); you get it
through the registry.

**Example usage:**

```python
from simplibs.extractor import DEFAULT_PROFILE_KEY, extract, get_profile

DEFAULT_PROFILE_KEY                                     # -> 'generic/all'
get_profile(DEFAULT_PROFILE_KEY).steps                  # -> None

extract(source="my_project")                            # the same as ...
extract(source="my_project", profile="generic/all")     # ... this
```

**Why it needs no rules.** The read phase drops binary files, so a profile that takes "everything" does not
have to say which files are text. What the profile leaves out are only the folders the scan itself skips
(version-control and cache folders and the like).

**It is registered when the registry is imported**, with `replace_existing=True`, so importing the package
again — or reloading it — never fails on its own profile.

<details>
<summary>🔍 Under the hood</summary>

```python
GENERIC_ALL: Final[Profile] = Profile(
    system="generic",
    name="all",
    description="Every text file, unchanged.",
)
```

```python
# registry/__init__.py — the one side effect of importing the package
register_profile(GENERIC_ALL, replace_existing=True)
```

```python
# resolve_profile — no profile chosen means the built-in one
if profile is None:
    return get_profile(DEFAULT_PROFILE_KEY)
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `register_renderer`

**Adds an output format** — a function that turns the entries into the text of the output.

**Parameters:**

| Name               | Type                  | Default | Description                                                                         |
|--------------------|-----------------------|---------|-------------------------------------------------------------------------------------|
| `name`             | `OutputFormat`        |         | The format name (`"markdown"`) — lowercase, starts with a letter.                   |
| `func`             | `Callable[..., str]`  |         | The renderer: it takes the entries and the render context and returns the output text. |
| `replace_existing` | `bool`                | `False` | Allow replacing a renderer that already has this name. *(keyword-only)*             |

**Returns:** `None`.

**Raises:**
`ParamError` (`EXTRACTOR_CONFIG_INVALID`) — the name is taken and `replace_existing` is `False`.
`ValidationError` — the name is not of the shape of a format name (`"Names"`, `""`, `"my format"`).

**Example usage:**

```python
from simplibs.extractor import GENERATED_MARKER, extract, list_formats, register_renderer

def render_names(entries, context):                     # entries in, text out
    names = "\n".join(entry.relative for entry in entries)
    return f"# {GENERATED_MARKER}\n{names}\n"           # the marker keeps this output out of the next run

register_renderer("names", render_names)

list_formats()                                          # -> ['markdown', 'names', 'plain']
extract(source="my_project", format="names", target="my_project/files.txt")

register_renderer("names", render_names)                # raises ParamError — the name is taken
register_renderer("names", render_names, replace_existing=True)   # fine
register_renderer("Names", render_names)                # raises ValidationError — a format name is lowercase
```

**One way to add a format.** The built-in formats are registered through this same function when the render
phase is imported, so the core never branches on a format name: a new format is one call and no change in the
library.

**The renderer signature** — what `entries` and `context` are, and what the output must contain — is described
with [the render phase](logic/README_EXTRACTOR_RENDER.md). The registry types it only as *"a callable returning
text"*, because it sits to the left of the render phase.

<details>
<summary>🔍 Under the hood</summary>

```python
@validate_call
def register_renderer(
    name: OutputFormat,
    func: Callable[..., str],
    *,
    replace_existing: bool = False,
) -> None:
    # 1. Refuse a taken name unless replacing was asked for
    if name in RENDERER_REGISTRY and not replace_existing:
        raise_renderer_exists_error(name)

    # 2. Store
    RENDERER_REGISTRY[name] = func
```

```python
# the built-in formats, registered by the render phase
register_renderer("markdown", render_markdown, replace_existing=True)
register_renderer("plain", render_plain, replace_existing=True)
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `get_renderer`

**Returns the renderer registered for a format name** — and is, at the same time, the **check that a format
exists**.

**Parameters:**

| Name   | Type  | Description                              |
|--------|-------|------------------------------------------|
| `name` | `str` | The format name (`"markdown"`).          |

**Returns:** the renderer function, a `Callable[..., str]`.

**Raises:**
`ParamError` (`EXTRACTOR_CONFIG_INVALID`) — no renderer has this name; the card lists the known formats.

**Example usage:**

```python
from pathlib import Path
from simplibs.extractor import Entry, RenderContext, get_renderer

render = get_renderer("plain")                          # the function that writes the plain format
context = RenderContext(title="Demo", source=Path("my_project"), profile_key="generic/all", add_tree=False)
text = render([Entry("a.py", ".py", "x = 1\n")], context)       # the output text, marker in its first line

get_renderer("html")                                    # raises ParamError — the card lists: markdown, plain
```

**Why it is also the format check.** `resolve_config` calls it before any file is read, so a typo in
`format=` fails in the first millisecond and not after a scan of the whole project.

<details>
<summary>🔍 Under the hood</summary>

```python
@validate_call
def get_renderer(name: str) -> Callable[..., str]:
    # 1. Look the name up
    renderer = RENDERER_REGISTRY.get(name)

    # 2. Unknown format: say what exists
    if renderer is None:
        raise_unknown_renderer_error(name)

    # 3. Found
    return renderer
```

```python
# resolve_config
# 5. The format must have a renderer (raises with the list of known formats)
get_renderer(output_format)
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `list_formats`

**Lists the registered output formats**, sorted.

**Parameters:** none.

**Returns:** a `list[str]`.

**Example usage:**

```python
from simplibs.extractor import list_formats

list_formats()                                          # -> ['markdown', 'plain']
```

**Why the command reads it.** The `--format` option of the command takes its choices from here instead of
from a fixed list — a format you register appears in the command's help without a change in the command.

<details>
<summary>🔍 Under the hood</summary>

```python
@validate_call
def list_formats() -> list[str]:
    # 1. Sorted names of the registered renderers
    return sorted(RENDERER_REGISTRY)
```

```python
# cli/build_parser.py
parser.add_argument("--format", choices=list_formats(), help="output format (default: the profile's)")
```

</details>

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../README.md#-profiles-registry-and-add-ons)
