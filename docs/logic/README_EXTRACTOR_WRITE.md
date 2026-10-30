# 💾 `logic/write` — Phase 5: Put It on the Disk

The fifth phase takes the finished text and **writes it to the output file** — by the overwrite policy, and
atomically. It is the only place where the extractor writes its output, and the only place where the
**dry run** has to be kept honest: a dry run makes exactly the decisions the real run would make and then
stops before the disk is touched.

```
rendered text + target + policy ──► directory? ──► exists and "error"? ──► numbered name? ──► dry run? ──► backup ──► write
                                      refuse           refuse                 "unique"          stop here    "backup"   atomic
```

The phase is a single function. Everything it needs to know — *what happens when the file exists* — is the
[`OverwritePolicy`](../README_EXTRACTOR_ANNOTATIONS.md#overwritepolicy) of the configuration.

```python
from pathlib import Path
from simplibs.extractor.logic import write_output

target = Path("out/extraction.md")

write_output(target, "# Extraction\n", "overwrite", dry_run=True)      # -> Path('out/extraction.md')   decided, nothing written
write_output(target, "# Extraction\n", "overwrite", dry_run=False)     # -> Path('out/extraction.md')   written (and out/ created)
```

In `extract()` the phase runs only if there is something to write. An extraction that selected nothing — or
whose every file failed — writes nothing and is unsuccessful; a file with just a title would hide a wrong
filter or a wrong folder.

**A write that fails raises.** Unlike a problem of one file, which is only a line in the report, a write that
fails means there is **no output at all** — so it is an exception (`AccessError` and the other cards of
`simplibs-file`, for example a refused permission). Inside `extract_many` the same failure becomes a result
with `fatal` set, and the other extractions still run.

## What is public

`write_output` is declared in the `__all__` of `simplibs.extractor.logic` and is **not** exported from the package root.
Your programs call `extract()`; it is documented here for readers who want to know exactly what each policy
does, for tools built on the extractor and for tests.

---

## 🧭 Table of Contents

* [`write_output`](#write_output)

[⬅️ Back to main README](../../README.md#-the-six-phases)

---

### `write_output`

**Writes the output according to the overwrite policy, or only plans the write.**

**Parameters:**

| Name      | Type              | Description                                                                              |
|-----------|-------------------|------------------------------------------------------------------------------------------|
| `target`  | `Path`            | The intended output file.                                                                |
| `text`    | `str`             | The rendered output.                                                                     |
| `policy`  | `OverwritePolicy` | What to do when `target` exists: `"overwrite"`, `"unique"`, `"backup"` or `"error"`.     |
| `dry_run` | `bool`            | If `True`, decide everything and write nothing.                                          |

**Returns:** the `Path` that **is** (or, in a dry run, **would be**) written. It differs from `target` only
under the `unique` policy.

**Raises:**
`StateError` (`EXTRACTOR_TARGET_IS_DIR`) — `target` is a directory (also in a dry run).
`AlreadyExistsError` (`EXTRACTOR_TARGET_EXISTS`) — `target` exists and the policy is `"error"` (also in a dry
run).
The cards of `simplibs-file` (`AccessError`, `ConversionError`, …) — the write itself fails.

**What each policy does:**

| Policy        | The output does **not** exist | The output **exists**                                                         | Returns                    |
|---------------|-------------------------------|-------------------------------------------------------------------------------|----------------------------|
| `"overwrite"` | it is written                 | it is **replaced**, atomically                                                | `target`                   |
| `"unique"`    | it is written                 | the old file stays; the new one is written under a **numbered name** (`extraction (1).md`) | the numbered path |
| `"backup"`    | it is written                 | the old file is **copied** to a backup next to it, then replaced              | `target`                   |
| `"error"`     | it is written                 | **refused** — `EXTRACTOR_TARGET_EXISTS`                                       | *(raises)*                 |

With `dry_run=True` every row gives the **same verdict** and the same returned path — only the writing and
the backup copy are left out.

**Example usage:**

```python
from pathlib import Path
from simplibs.extractor.logic import write_output

target = Path("out/extraction.md")

# 1. The first write creates the folder as well
write_output(target, "first\n", "overwrite", dry_run=False)         # -> Path('out/extraction.md')

# 2. overwrite: the file is replaced
write_output(target, "second\n", "overwrite", dry_run=False)        # out/extraction.md now holds 'second'

# 3. unique: the old file is left alone, a numbered one is written
write_output(target, "third\n", "unique", dry_run=False)            # -> out/extraction (1).md    out/extraction.md still holds 'second'

# 4. backup: the old output is kept as a copy, then replaced
write_output(target, "fourth\n", "backup", dry_run=False)           # -> Path('out/extraction.md')
                                                                    #    a copy such as out/extraction_20261030_101500.md.bak appeared next to it

# 5. error: refuses an existing output
write_output(target, "fifth\n", "error", dry_run=False)             # raises AlreadyExistsError

# 6. A dry run gives the same verdicts and writes nothing
write_output(target, "x\n", "unique", dry_run=True)                 # -> the numbered path that WOULD be written
write_output(target, "x\n", "error", dry_run=True)                  # raises AlreadyExistsError — also in a dry run
write_output(Path("out"), "x\n", "overwrite", dry_run=True)         # raises StateError — 'out' is a directory
```

**The order of the checks.** Each step can end the function; the order is what makes a dry run trustworthy.

| #   | Step                                                                        | In a dry run |
|----:|-----------------------------------------------------------------------------|:------------:|
| 1   | A directory in the way → `EXTRACTOR_TARGET_IS_DIR`                          | ✅ checked    |
| 2   | The output exists and the policy is `error` → `EXTRACTOR_TARGET_EXISTS`     | ✅ checked    |
| 3   | `unique` and the output exists → choose the numbered name                   | ✅ decided    |
| 4   | **A dry run stops here and returns the path.**                              |              |
| 5   | `backup` and the output exists → copy the old output                        | ❌ skipped    |
| 6   | Write the text (atomically; the folder is created if missing)               | ❌ skipped    |

**Why a dry run gives the same verdicts.** A dry run reports what the real run **would** do. If a directory in
the way or the `error` policy were noticed only by the real write, the dry run would promise a result that
never happens — worse than no dry run at all.

**The write is atomic.** The text goes to a draft file first and is swapped in when complete, so a run that
stops halfway leaves the previous output intact. A draft that stays behind after a crash is never mistaken for
input: its name is in the default ignore set of the scan.

**Backups are copies with the marker.** `backup_file` copies the old output as it is — **marker included** — so
the next scan recognizes the backup as generated and skips it. A backup is never overwritten by another backup:
two in the same second get a numbered variant.

**Raw text.** The output is written exactly as it was rendered: UTF-8 **without** a byte-order mark and with
`"\n"` line endings, the same on every platform.

<details>
<summary>🔍 Under the hood</summary>

```python
def write_output(
    target: Path,
    text: str,
    policy: OverwritePolicy,
    dry_run: bool,
) -> Path:

    # 1. A directory can never be the output, real run or not
    if target.is_dir():
        raise_target_is_dir_error(target)

    # 2. The `error` policy fails before anything else, also in a dry run
    exists = target.exists()
    if exists and policy == "error":
        raise_target_exists_error(target)

    # 3. `unique` writes next to the existing file under a numbered name
    final = make_unique_path(target) if exists and policy == "unique" else target

    # 4. A dry run stops here: the decision is made, the disk is untouched
    if dry_run:
        return final

    # 5. `backup` keeps the old file before it is replaced
    if exists and policy == "backup":
        backup_file(target)

    # 6. The write itself is atomic (draft and swap); the folder is created if missing
    write_text(final, text)
    return final
```

`make_unique_path` only **looks** — it never creates anything — which is why it may run in a dry run.
`backup_file` and `write_text` are the functions of [`simplibs-file`](https://pypi.org/project/simplibs-file/);
`write_text` encodes first, so a text that cannot be encoded fails with the disk untouched.

</details>

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../../README.md#-the-six-phases)
