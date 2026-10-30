# 🔌 `plugins` — Finding Add-Ons

The extractor knows **no language and no kind of project** — on its own it only has the profile `generic/all`.
What a Python project, a React project or your own kind of project needs — which files, which cleaning —
comes from **add-ons**: separate packages that register **profiles** (and, if they want, output formats) in the
[registry](README_EXTRACTOR_REGISTRY.md).

The `plugins` package is the half that **finds** them. It holds one function, `load_plugins`, which looks up
every installed add-on and lets it register itself.

```
pip install simplibs-code-extractor
        │
        ▼
 entry point in the group "simplibs.extractor.plugins"
        │      code = "simplibs.code_extractor:register_all"
        ▼
 load_plugins() ──► calls register_all() ──► register_profile(...)  ──►  the registry
```

Installing the package is the whole installation: the next `simplibs-extractor --list-systems` already shows
the add-on's systems, and nothing has to be imported by name.

```python
from simplibs.extractor import list_systems, load_plugins

list_systems()                                          # -> ['generic']
loaded, failed = load_plugins()                         # every installed add-on registers its profiles
list_systems()                                          # -> ['generic', 'python', 'react']      with simplibs-code-extractor installed
```

## Using add-ons

| Where you work       | What you do                                                                                              |
|----------------------|----------------------------------------------------------------------------------------------------------|
| **the command line** | `pip install` the add-on. The command loads add-ons itself, before its parser is built; one that fails to load is a **warning**, not a stop. |
| **Python**           | `pip install` the add-on and call `load_plugins()` once, before you look a profile up. `extract()` does **not** load add-ons by itself. |

## Writing an add-on

An add-on is an ordinary package with **one function** and **one entry point**.

**1. The function.** It takes no arguments and registers what the add-on brings:

```python
# shell_extractor/__init__.py
from simplibs.extractor import Profile, register_profile
from simplibs.path.rules import HasSuffix, ParentNameIs

def register_all() -> None:
    register_profile(
        Profile(
            system="shell",
            name="scripts",
            description="Shell scripts, without the tests folder.",
            include=HasSuffix(".sh"),
            exclude=ParentNameIs("tests"),
            output_name="shell_scripts.md",
        ),
        replace_existing=True,                          # see the rules below
    )
```

**2. The entry point**, in the add-on's own `pyproject.toml`:

```toml
[project]
name = "shell-extractor"
dependencies = ["simplibs-extractor>=0.1.0"]

[project.entry-points."simplibs.extractor.plugins"]
shell = "shell_extractor:register_all"
```

The name on the left (`shell`) is how `load_plugins` refers to the add-on in its answer; the value is
`module:function`.

**3. Done.** After `pip install shell-extractor`:

```text
simplibs-extractor --list-systems                       # shell
simplibs-extractor shell scripts my_project             # -> my_project/shell_scripts.md
```

**The rules of a good `register_all`:**

| Rule                                                           | Why                                                                                                   |
|----------------------------------------------------------------|-------------------------------------------------------------------------------------------------------|
| It takes **no arguments**.                                     | `load_plugins` calls it as `entry_point.load()()`.                                                    |
| It registers with **`replace_existing=True`**.                 | Calling `load_plugins()` twice (a second command in one process, a reload, a test) must change nothing. Without it the second call finds the key taken and the add-on lands in `failed`. |
| It only **registers** — profiles and, if needed, renderers.    | It runs on every start of the command; no scans, no network, no printing.                             |
| It uses the **public API** only (`Profile`, `register_profile`, `register_renderer`, `GENERATED_MARKER`). | The add-on then keeps working when the inside of the extractor changes. |
| It stays **quick and quiet**.                                  | A slow add-on slows every command; a loud one prints into every run.                                  |

**A failing add-on never stops the others.** An error in `register_all` — or in importing the add-on — is
caught, and the add-on appears in the `failed` part of the answer with a one-line reason. The command line
turns it into a warning and goes on.

---

## 🧭 Table of Contents

* [`load_plugins`](#load_plugins)

[⬅️ Back to main README](../README.md#-profiles-registry-and-add-ons)

---

### `load_plugins`

**Finds the installed add-ons and lets each register its profiles.**

Every entry point of the group names a function that takes no arguments and registers profiles (and renderers)
in the extractor's registry.

**Parameters:**

| Name           | Type       | Default                        | Description                                                                                  |
|----------------|------------|--------------------------------|----------------------------------------------------------------------------------------------|
| `group`        | `str`      | `"simplibs.extractor.plugins"` | The entry-point group. *(keyword-only)*                                                      |
| `entry_points` | callable   | `None`                         | A replacement for `importlib.metadata.entry_points`, called as `entry_points(group=group)` — for tests. *(keyword-only)* |

**Returns:** a pair `(loaded, failed)`:

| Part     | Type             | Description                                                                          |
|----------|------------------|--------------------------------------------------------------------------------------|
| `loaded` | `list[str]`      | The names of the add-ons that loaded.                                                |
| `failed` | `dict[str, str]` | `{name: one-line reason}` of the add-ons that did not.                               |

**Raises:** nothing for an add-on's own problems — whatever its code does, the add-on lands in `failed`.

**Example usage:**

```python
from simplibs.extractor import extract, list_profiles, load_plugins

# 1. The real lookup
loaded, failed = load_plugins()
loaded                                                  # -> ['code']        with simplibs-code-extractor installed
failed                                                  # -> {}

[profile.key for profile in list_profiles("python")]    # the add-on's profiles are there now
extract(source="my_project", profile="python/code-clean")

# 2. A failing add-on is reported, the others still load
for name, reason in failed.items():
    print(f"add-on {name!r} did not load: {reason}")

# 3. Safe to call twice — an add-on registers with replace_existing=True, so nothing changes
load_plugins()
load_plugins()

# 4. Your own application with its own group
load_plugins(group="my_app.extractor_plugins")
```

**Testing an add-on — or the loader — without installing anything.** `entry_points` replaces the real lookup;
it is called as `entry_points(group=group)` and returns objects with a `name` and a `load()`:

```python
from types import SimpleNamespace
from simplibs.extractor import load_plugins

def good() -> None:
    ...                                                 # registers profiles

def broken() -> None:
    raise RuntimeError("boom")

fake = lambda *, group: [
    SimpleNamespace(name="good", load=lambda: good),
    SimpleNamespace(name="broken", load=lambda: broken),
]

loaded, failed = load_plugins(entry_points=fake)
loaded                                                  # -> ['good']
failed                                                  # -> {'broken': 'RuntimeError: boom'}
```

**Why failures are returned and not logged.** A broken add-on should not take the tool down, and the person
should still hear about it. The function reports; the caller — the command line — decides how to say it.

**The second broad `except`.** As in the per-file loop of the run: the code is somebody else's, and *"this
add-on does not load"* is the useful answer whatever the cause — a missing dependency, a typo in the entry
point, an error in `register_all`.

**Why `pip install` is enough.** The profiles of every installed add-on exist **without the extractor knowing
any of them by name**. The entry-point group is the agreement; see
[`PLUGIN_GROUP`](README_EXTRACTOR_CONSTANTS.md#plugin_group).

<details>
<summary>🔍 Under the hood</summary>

```python
def load_plugins(
    *,
    group: str = PLUGIN_GROUP,
    entry_points=None,
) -> tuple[list[str], dict[str, str]]:

    # 1. The real lookup, unless a test supplies its own
    finder = entry_points or importlib.metadata.entry_points

    # 2. Load and run each add-on; its code is foreign, so any error of it is its own
    loaded: list[str] = []
    failed: dict[str, str] = {}
    for entry_point in finder(group=group):
        try:
            entry_point.load()()
        except Exception as exc:
            failed[entry_point.name] = describe_failure(exc)
        else:
            loaded.append(entry_point.name)

    return loaded, failed
```

`entry_point.load()` imports the module and returns the function named in the entry point; the second pair of
parentheses calls it. A failure of either — the import or the call — lands in `failed`, described in one line
by the same helper that describes a failed file.

The command line calls it before it builds its parser, so `--list-systems` and `--list-profiles` already see
the add-ons' profiles:

```python
# cli/run_cli.py
loaded, failed = load_plugins()
```

</details>

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../README.md#-profiles-registry-and-add-ons)
