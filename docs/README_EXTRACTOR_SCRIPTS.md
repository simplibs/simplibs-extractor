# 📜 `scripts` — The Extractor Inside a Project Folder

The `scripts` package puts the extractor **into a project**: a two-line script that lies in the folder it
should extract, says only *which profile*, and needs no command line, no paths and no configuration. Where the
script lies **is** the source; the output goes next to it; the script itself is never part of its own output.

```python
# extract_here.py — dropped into a project folder (or: simplibs-extractor init my_project)
from simplibs.extractor import extract_here

extract_here(__file__, profile="python/code-clean")
```

Running it (`python extract_here.py`) prints the summary of the run and writes the output next to the script.

The package has three functions:

| Function                | What it does                                                                | Touches the disk |
|-------------------------|-----------------------------------------------------------------------------|:----------------:|
| `extract_here`          | extracts the folder of a script into a file next to it — the whole script in one call | reads and writes (through `extract`) |
| `generate_local_script` | writes a ready-to-run `extract_here.py` into a folder                       | writes           |
| `render_script`         | fills the script template and returns its text                              | no               |

`extract_here` and `generate_local_script` are exported from the package root; `render_script` is importable
from `simplibs.extractor.scripts`.

```
generate_local_script ──► render_script ──► SCRIPT_TEMPLATE.format(...) ──► extract_here.py
   (writes the file)        (the text)         (constants)                       │
                                                                                 ▼  python extract_here.py
                                                                            extract_here(__file__, profile=...)
                                                                                 │
                                                                                 ▼
                                                                              extract(...)  ──► my_project/<output>
```

## The one function of the library that prints

Every other function of the library is silent: it returns a result and leaves the printing to the caller.
`extract_here` is the exception — a script has no one to print for it, so this entry point shows the summary
itself, **unless you pass `quiet=True`**. The headline is green for a success and red otherwise; the colors
switch themselves off when the output is not a terminal (a pipe, a file, a log).

---

## 🧭 Table of Contents

* [`extract_here`](#extract_here)
* [`generate_local_script`](#generate_local_script)
* [`render_script`](#render_script)
* [`print_result`](#print_result) *(private helper)*

[⬅️ Back to main README](../README.md#-scripts--two-lines-in-a-folder)

---

### `extract_here`

**Extracts the folder a script lies in, into a file next to the script** — the whole script in one call.

**Parameters:**

| Name          | Type                      | Default | Description                                                                                          |
|---------------|---------------------------|---------|------------------------------------------------------------------------------------------------------|
| `anchor`      | `PathLike`                |         | `__file__` of the script — its folder is the source and the script itself is left out — or a folder. |
| `profile`     | `Profile \| str \| None`  | `None`  | A `Profile`, a registered key, or `None` for `generic/all`.                                          |
| `output_name` | `str \| None`             | `None`  | The output file name; by default the profile's. *(keyword-only)*                                      |
| `quiet`       | `bool`                    | `False` | If `True`, print nothing. *(keyword-only)*                                                            |
| `logger`      | `Any`                     | `None`  | Where progress goes (see [`extract`](logic/README_EXTRACTOR_RUN.md#extract)). *(keyword-only)*       |
| `**overrides` | `Any`                     |         | Any other field of `ExtractionConfig`; these **win** over what is derived here.                      |

**Returns:** the [`ExtractionResult`](README_EXTRACTOR_DEFINITIONS.md#extractionresult) of the extraction.

**Raises:**
`ParamError` (`EXTRACTOR_CONFIG_INVALID`) — `output_name` is not a plain file name; anything else `extract`
refuses.
`NotFoundError` (`EXTRACTOR_PROFILE_NOT_FOUND`, `EXTRACTOR_SOURCE_NOT_FOUND`) — an unknown profile, or an
`anchor` that is neither a file nor a folder.

**Example usage:**

```python
from pathlib import Path
from simplibs.extractor import extract_here

# 1. The two-line script
extract_here(__file__, profile="python/code-clean")     # source = this folder, output next to the script

# 2. The default profile, a chosen output name
extract_here(__file__)                                  # generic/all -> extraction.md
extract_here(__file__, profile="python/code-clean", output_name="code.md")

# 3. Say nothing, use the result yourself
result = extract_here(__file__, quiet=True)
result.success                                          # -> True

# 4. Your own values win over the derived ones
extract_here(__file__, recursive=False)                 # only the files next to the script
extract_here(__file__, target=Path(__file__).parent / "out" / "all.md")     # another place for the output

# 5. A folder works as the anchor, too
extract_here("my_project")                              # output in my_project; there is no script to leave out

# 6. A name, not a path
extract_here(__file__, output_name="out/all.md")        # raises ParamError — a file name, not a path
```

What a run prints:

```text
Extraction: generic/all
  source : /home/me/my_project
  target : /home/me/my_project/extraction.md (written)
  files  : 4 ok, 1 skipped, 0 errors
  size   : 133 B in -> 502 B out (~115 tokens)
  skipped: logo.png (not a text file)
```

**What is derived, and what wins.** The function fills in what follows from where the script lies; **what you
pass replaces it**:

| Derived value | From                                           | Replaced by                |
|---------------|------------------------------------------------|----------------------------|
| `source`      | the folder of `anchor` (the anchor itself if it is a folder) | `source=...` |
| `target`      | `source / output_name` (the profile's name unless `output_name` is given) | `target=...` |
| `profile`     | the resolved profile                           | —                          |
| `skip_paths`  | the script itself, when `anchor` is a file     | **extended**, never replaced — your own `skip_paths` are kept **and** the script stays out |

The script must stay out of its own output, whatever else you pass — so `skip_paths` is the one value that is
added to and not replaced.

**`output_name` is a name, not a path.** The output always lies in the script's folder. A full path belongs to
`target=...`. The name is checked even if you also give a `target`.

**Why the profile is resolved first.** Its output name is needed to build the target, and a typo in a profile
key should fail **first**, before anything else is done.

**Why it prints.** A script is run by a person who wants to see what happened. The library functions stay
silent so that programs can decide for themselves; this entry point is for scripts, which cannot.

**Why it is not wrapped in `@validate_call`.** The inputs are checked where they are used: the profile by the
registry, the file name here, everything else by `ExtractionConfig`.

<details>
<summary>🔍 Under the hood</summary>

```python
def extract_here(
    anchor: PathLike,
    profile: Profile | str | None = None,
    *,
    output_name: str | None = None,
    quiet: bool = False,
    logger: Any = None,
    **overrides: Any,
) -> ExtractionResult:

    # 1. Where we are: a file means "its folder", a folder means itself
    anchor_path = normalize_path(anchor)
    is_file = anchor_path.is_file()
    root = anchor_path.parent if is_file else anchor_path

    # 2. The profile is resolved now: its output name is needed and a typo should fail first
    chosen = resolve_profile(profile)

    # 3. A file name, not a path: the output always lies in the script's folder
    name = output_name if output_name is not None else chosen.output_name
    if not is_valid_filename(name):
        raise_invalid_output_name_error(name)

    # 4. Derived values first, then the caller's own; the script is never its own input
    skipped = tuple(overrides.pop("skip_paths", ())) + ((anchor_path,) if is_file else ())
    params: dict[str, Any] = {
        "source": root,
        "target": root / name,
        "profile": chosen,
        "skip_paths": skipped,
    }
    params.update(overrides)

    # 5. Run, then show the outcome unless asked not to
    result = extract(logger=logger, **params)
    if not quiet:
        print_result(result)
    return result
```

An `anchor` that does not exist is treated as a folder, so the run ends with `EXTRACTOR_SOURCE_NOT_FOUND` — the
same card a missing source gets anywhere else.

</details>

[▲ Back to top](#-table-of-contents)

---

### `generate_local_script`

**Writes a ready-to-run local extraction script.** A project gets a script it can run without remembering any
command line. On the command line the same is `simplibs-extractor init`.

**Parameters:**

| Name        | Type                     | Default | Description                                                                        |
|-------------|--------------------------|---------|------------------------------------------------------------------------------------|
| `path`      | `PathLike`               |         | The script file (`*.py`), or an **existing** folder, which gets `extract_here.py`. |
| `profile`   | `Profile \| str \| None` | `None`  | A `Profile`, a registered key, or `None` for `generic/all`.                        |
| `overwrite` | `bool`                   | `False` | Replace the script if it already exists. *(keyword-only)*                           |

**Returns:** the `Path` of the written script (normalized and absolute).

**Raises:**
`ParamError` (`EXTRACTOR_CONFIG_INVALID`) — the file name does not end with `.py`.
`NotFoundError` (`EXTRACTOR_PROFILE_NOT_FOUND`) — the profile is not registered.
`AlreadyExistsError` — the script exists and `overwrite` is `False`. This is the card of `simplibs-file`, not
one of the extractor's.

**Example usage:**

```python
from simplibs.extractor import generate_local_script

generate_local_script("my_project")                     # -> Path('/home/me/my_project/extract_here.py')   a folder gets the default name
generate_local_script("my_project/run_extraction.py", profile="python/code-clean")     # an explicit name wins

generate_local_script("my_project")                     # raises AlreadyExistsError — the script exists; it may have been edited
generate_local_script("my_project", overwrite=True)     # fine — replacing was asked for

generate_local_script("my_project/run_extraction.txt")  # raises ParamError — it could not be run
generate_local_script("my_project", profile="python/nope")      # raises NotFoundError — nothing is written
```

The result, for `profile="python/code-clean"`, is the script from the top of this page:

```python
#!/usr/bin/env python3
"""Local extraction of this folder. Generated by simplibs-extractor.

Run it with:  python extract_here.py
"""
from simplibs.extractor import extract_here

if __name__ == "__main__":
    extract_here(__file__, profile='python/code-clean')
```

**An existing script is not replaced quietly.** It may have been edited. `overwrite=True` has to be asked for,
and the card that refuses is the one `simplibs-file` already raises.

**Only the profile's key is stored, not the profile.** The script has to work in a Python where the profile's
add-on is installed, and fail clearly where it is not. A one-off profile that was never registered therefore
cannot be used from a generated script — register it first.

**Why the profile is resolved first.** So that a typo in the key fails **before** anything is written.

**A folder must exist.** A path that is not an existing folder is taken as a file name, and a name without
`.py` is refused.

<details>
<summary>🔍 Under the hood</summary>

```python
def generate_local_script(
    path: PathLike,
    profile: Profile | str | None = None,
    *,
    overwrite: bool = False,
) -> Path:

    # 1. A folder means "the default name in it"
    target = normalize_path(path)
    if target.is_dir():
        target = target / DEFAULT_SCRIPT_NAME

    # 2. It has to be a Python file, or it could not be run
    if target.suffix != ".py":
        raise_not_python_script_error(target)

    # 3. The profile is resolved now, so a typo fails before anything is written
    key = resolve_profile(profile).key

    # 4. Written atomically; `overwrite=False` makes the file library refuse an existing script
    return write_text(target, render_script(target.name, key), overwrite=overwrite)
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `render_script`

**Fills the script template** and returns the source text of the script — with no access to the disk.

**Parameters:**

| Name          | Type  | Description                                                                            |
|---------------|-------|----------------------------------------------------------------------------------------|
| `file_name`   | `str` | The name the script will have — shown in its *"Run it with"* line.                     |
| `profile_key` | `str` | The profile the script extracts with (`"python/code-clean"`).                          |

**Returns:** the source text of the script, as a `str`.

**Example usage:**

```python
from simplibs.extractor.scripts import render_script

text = render_script("extract_here.py", "python/code-clean")
print(text)                                             # the script shown above

compile(text, "extract_here.py", "exec")                # it is valid Python — no disk, no run
```

**Why it is separate.** The text of the script can be **tested** — compiled, even run — without touching the
disk, while `generate_local_script` only adds the decisions about *where* and *whether to overwrite*.

**Why `!r`.** The profile key is written as a Python literal, quotes included, so no key can break the
generated code. The template itself is the constant
[`SCRIPT_TEMPLATE`](README_EXTRACTOR_CONSTANTS.md#script_template).

<details>
<summary>🔍 Under the hood</summary>

```python
def render_script(file_name: str, profile_key: str) -> str:

    # 1. `{profile!r}` writes the key as a Python literal, so no key can break the code
    return SCRIPT_TEMPLATE.format(file_name=file_name, profile=profile_key)
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `print_result`

*Private helper.* **Prints the summary of a result; the first line is green on success and red otherwise.**

It is the one place where the library prints, and only for the scripts. The text itself is built by the same
[`format_summary`](logic/README_EXTRACTOR_REPORT.md#format_summary) every other caller uses; only the
headline gets a color.

**Colors without conditions.** `simplibs-style` writes plain text in a pipe, a file or a log, so there is no
`isatty` check here.

<details>
<summary>🔍 Under the hood</summary>

```python
def print_result(result: ExtractionResult) -> None:

    # 1. Build the text with the same function every other caller uses
    head, _, rest = format_summary(result).partition("\n")

    # 2. Color only the headline; `style` turns itself off when the output is not a terminal
    paint = SUCCESS if result.success else ERROR
    print(paint(head) + (f"\n{rest}" if rest else ""))
```

</details>

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../README.md#-scripts--two-lines-in-a-folder)
