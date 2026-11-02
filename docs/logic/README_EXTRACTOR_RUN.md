# 🏃 `logic` — Putting the Phases Together

The run — three functions in the root of `logic`, above the six phase packages — is the **entry point of the library**: `extract()` runs one extraction through all six
phases, `extract_many()` runs several in a row, and `failure_result()` turns a run that could not start into a
result. Nothing here has logic of its own — each phase is a function with its own tests, and the run only wires
them in order.

```
extract(config, **overrides)
   │
   ├─ 1. resolve_config ───► Resolved                 everything that can fail, before any file is touched
   ├─ 2. select_sources ───► [paths]                  which files
   ├─ 3. for each path:  process_source               read, then transform — a bad file is a report, never fatal
   │        └─ read_source ─► apply_steps ─► (FileReport, Entry | None)
   ├─ 4. render + write_output   (only if there is an Entry)
   └─ 5. ExtractionResult ◄──── reports, sizes, a token estimate
```

```python
from simplibs.extractor import extract, format_summary

result = extract(source="my_project")                   # everything with defaults: generic/all, Markdown, my_project/extraction.md
print(format_summary(result))
```

| Phase     | Called by the run as                  | Reference                                                   |
|-----------|---------------------------------------|-------------------------------------------------------------|
| Select    | `resolve_config`, `select_sources`    | [SELECT](README_EXTRACTOR_SELECT.md)                        |
| Read      | `read_source` (inside `process_source`) | [READ](README_EXTRACTOR_READ.md)                          |
| Transform | `apply_steps` (inside `process_source`) | [TRANSFORM](README_EXTRACTOR_TRANSFORM.md)                |
| Render    | the renderer of the format            | [RENDER](README_EXTRACTOR_RENDER.md)                        |
| Write     | `write_output`                        | [WRITE](README_EXTRACTOR_WRITE.md)                          |
| Report    | `estimate_tokens`, then `ExtractionResult` | [REPORT](README_EXTRACTOR_REPORT.md)                   |

## Two kinds of failure, two behaviours

| What fails                                                                    | What happens                                                              |
|-------------------------------------------------------------------------------|---------------------------------------------------------------------------|
| A **configuration that cannot run** — an unknown parameter, a missing source, an unknown profile or format | a card is **raised**, before any file is read |
| **One file** that cannot be read or transformed                               | a line in the result (`status="error"`); the run continues                |
| **One file** that a step could not process fully (the step warned)            | a line in the result (`status="partial"`); the file stays in the output   |
| A **write** that fails, or is refused by the `error` policy                   | a card is **raised** — there is no output at all                          |
| Nothing was selected, or every file failed                                    | nothing is written; the result is **unsuccessful** (`success` is `False`) |

An extraction that selected nothing is almost always a wrong filter or a wrong folder, and a file with just a
title would hide it — which is why it writes nothing and says so.

## Nothing is printed

Progress goes to the **logger** you pass, if any; the outcome goes into the **result**. The run never prints,
never creates a logger and never colors anything — the command turns the result into a summary and an exit
code, and a script or an application does whatever it needs.

| Message                                      | Level                                  | When                                  |
|----------------------------------------------|----------------------------------------|---------------------------------------|
| `Extracting <source> with profile <key>`     | info                                   | after the configuration is resolved   |
| `Selected N file(s)`                         | info                                   | after the select phase                |
| `<path>: ok` / `<path>: skipped (<reason>)`  | debug                                  | for every file that is ok or skipped  |
| `<path>: error (<reason>)`                   | warning                                | for every failed file, and `<path>: partial (<reason>)` for a partial one |
| `Nothing to extract - no file was written`   | warning                                | no file made it into the output       |
| `Done: <target>`                             | success — or warning if unsuccessful   | at the end                            |

## What is public

`extract` and `extract_many` are exported from the package root. `failure_result` is declared in the
`__all__` of `simplibs.extractor.logic`; the helpers in `logic/_helpers` (and `logic/_common`) are private.

---

## 🧭 Table of Contents

**Running**

* [`extract`](#extract)
* [`extract_many`](#extract_many)
* [`failure_result`](#failure_result)

**Private helpers**

* [`process_source`](#process_source)
* [`RunLog`](#runlog)
* [`build_title`](#build_title)

[⬅️ Back to main README](../../README.md#-running-an-extraction)

---

### `extract`

**Runs one extraction through all six phases** — select, read, transform, render, write, report.

It takes a ready `ExtractionConfig`, plain keyword values, or both: the keywords then change a **copy** of the
config, and the original is untouched.

**Parameters:**

| Name          | Type                       | Default | Description                                                                                  |
|---------------|----------------------------|---------|----------------------------------------------------------------------------------------------|
| `config`      | `ExtractionConfig \| None` | `None`  | A ready config, or `None` to build one from the keywords.                                    |
| `logger`      | `Any`                      | `None`  | Where progress goes: a `SimpleLogger`, a standard `logging.Logger`, or `None` for silence. *(keyword-only)* |
| `**overrides` | `Any`                      |         | Any field of [`ExtractionConfig`](../README_EXTRACTOR_DEFINITIONS.md#extractionconfig) to set or to change. |

**Returns:** an [`ExtractionResult`](../README_EXTRACTOR_DEFINITIONS.md#extractionresult) — per-file reports,
sizes, the output path and whether anything was written. Problems with single files are **inside** it.

**Raises:**
`ParamError` (`EXTRACTOR_CONFIG_INVALID`) — an unknown parameter, no source, an unknown format.
`NotFoundError` (`EXTRACTOR_SOURCE_NOT_FOUND`, `EXTRACTOR_PROFILE_NOT_FOUND`) — the source is not a folder, or
the profile is not registered.
`ValidationError` — a value has the wrong type (`overwrite="clobber"`).
`AlreadyExistsError` (`EXTRACTOR_TARGET_EXISTS`), `StateError` (`EXTRACTOR_TARGET_IS_DIR`), `AccessError`,
`ConversionError` — from the write, when the output cannot be written.

**Example usage:**

```python
from simplibs.extractor import ExtractionConfig, extract
from simplibs.path.rules import HasSuffix

# 1. Keywords only
result = extract(source="my_project")
result = extract(source="my_project", profile="python/code-clean", dry_run=True)

# 2. A ready config
config = ExtractionConfig(source="my_project", profile="python/code-clean", include=HasSuffix(".py"))
result = extract(config)

# 3. Both: the keywords change a copy of the config
result = extract(config, dry_run=True, add_tree=False)          # `config` itself is not changed

# 4. What came back
result = extract(source="my_project", dry_run=True)
result.success                                          # -> True
result.target.name                                      # -> 'extraction.md'
[f.relative for f in result.ok_files]                   # -> ['README.md', 'src/app.py', 'src/config.py', 'tests/test_app.py']

# 5. A configuration that cannot run raises before any file is touched
extract(sourse="my_project")                            # raises ParamError — the card lists every valid parameter
extract(source="no_such_folder")                        # raises NotFoundError
extract(source="my_project", profile="python/nope")     # raises NotFoundError — the card lists the registered keys

# 6. A file that cannot be used is a line in the result, not an exception
[(f.relative, f.reason) for f in result.skipped_files]  # -> [('logo.png', 'not a text file')]
```

**`result.target` is the path that was really written.** Under the `unique` policy it is the numbered name
(`extraction (1).md`), not the one you configured. In a dry run it is the path that **would** be written.

**Nothing selected writes nothing.** `result.written` is `False`, `result.files` is empty, `result.success`
is `False` and `result.target` is the planned path. The same holds when every selected file failed.

**Progress goes to a logger of your choice:**

```python
import logging
from simplibs.extractor import extract

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
extract(source="my_project", logger=logging.getLogger("extractor"))
```

```text
INFO Extracting /home/me/my_project with profile generic/all
INFO Selected 5 file(s)
DEBUG logo.png: skipped (not a text file)
DEBUG src/app.py: ok
...
INFO Done: /home/me/my_project/extraction.md
```

A standard `logging.Logger` works as it is (the *success* message is written as `info`), and so does a
`SimpleLogger` of `simplibs-logger`.

**Why it only wires.** Each phase is a function with its own tests; the run just calls them in order. That
keeps the rule *"one bad file never stops the run"* in one place and the entry point short enough to read in
one go.

**Why it is not wrapped in `@validate_call`.** The inputs arrive as keyword overrides that become an
`ExtractionConfig`, whose own `@validate_dataclass` checks every field. A second layer in front would only
check the same values twice.

<details>
<summary>🔍 Under the hood</summary>

```python
def extract(
    config: ExtractionConfig | None = None,
    *,
    logger: Any = None,
    **overrides: Any,
) -> ExtractionResult:
    started = time.perf_counter()
    log = RunLog(logger)

    # 1. Resolve and check everything that can fail before any file is touched
    plan = resolve_config(config, overrides)
    cfg, profile = plan.config, plan.profile
    log.info("Extracting %s with profile %s", cfg.source, profile.key)

    # 2. Select
    paths = select_sources(plan)
    log.info("Selected %d file(s)", len(paths))

    # 3. Read and transform, file by file; a bad file is reported, never fatal
    reports: list[FileReport] = []
    entries: list[Entry] = []
    for path in paths:
        report, entry = process_source(path, plan)
        if entry is not None:
            entries.append(entry)
        reports.append(report)
        if report.status in ("error", "partial"):
            log.warning("%s: %s (%s)", report.relative, report.status, report.reason)
        else:
            log.debug("%s: %s%s", report.relative, report.status, f" ({report.reason})" if report.reason else "")

    # 4. Render and write — only when there is something to write
    rendered = ""
    written = False
    target = cfg.target
    if entries:
        context = RenderContext(build_title(cfg), cfg.source, profile.key, cfg.add_tree)
        rendered = get_renderer(plan.format)(entries, context)
        target = write_output(cfg.target, rendered, cfg.overwrite, cfg.dry_run)
        written = not cfg.dry_run
    else:
        log.warning("Nothing to extract - no file was written")

    # 5. Report
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
    (log.success if result.success else log.warning)("Done: %s", target)
    return result
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `extract_many`

**Runs several extractions one after another.** A run that cannot start or cannot write does **not** stop the
others: it appears in the list as a result with `fatal` set.

**Parameters:**

| Name            | Type                        | Default | Description                                                                     |
|-----------------|-----------------------------|---------|---------------------------------------------------------------------------------|
| `configs`       | `Sequence[ExtractionConfig]`|         | The configurations, in the order to run them.                                   |
| `logger`        | `Any`                       | `None`  | Where progress goes (see [`extract`](#extract)). *(keyword-only)*               |
| `stop_on_error` | `bool`                      | `False` | Stop after the first run that failed. *(keyword-only)*                          |

**Returns:** a `list[ExtractionResult]` — one result per run that was **started**, in the order of the
configs.

**Raises:**
`ValidationError` — `configs` is not a sequence of `ExtractionConfig` objects.

**Example usage:**

```python
from simplibs.extractor import ExtractionConfig, extract_many

configs = [
    ExtractionConfig(source="my_project", profile="generic/all"),
    ExtractionConfig(source="my_project", profile="python/nope"),                  # a typo — this run cannot start
    ExtractionConfig(source="my_project", profile="generic/all", target="my_project/second.md"),
]

results = extract_many(configs)
[result.success for result in results]                  # -> [True, False, True]     the broken run did not stop the third
results[1].fatal                                        # -> 'NotFoundError: ...'    one line
results[1].target                                       # -> None                    nothing was planned or written

for config, result in zip(configs, results):            # the order is the order of the configs
    print(config.profile, result.success)

# stop after the first run that failed
results = extract_many(configs, stop_on_error=True)
len(results)                                            # -> 2       the third was never started
```

**What "failed" means.** A run that raised a card of this library: a configuration that cannot run, or a write
that fails. An extraction in which some files failed — or in which nothing was selected — is an ordinary
**unsuccessful result**, not a failed run; it does not trigger `stop_on_error`.

**What is caught, and what is not.** Only the library's own cards (`SimpleException`). A bug in the code, or
in a step of a profile that escaped, is not a *"failed run"* and keeps its traceback.

**Why it exists.** `simplibs-extractor python code-clean,data-all` is **two extractions**. A typo in the
second profile must not throw away the first one's output — and the report should still list both.

<details>
<summary>🔍 Under the hood</summary>

```python
@validate_call
def extract_many(
    configs: Sequence[ExtractionConfig],
    *,
    logger: Any = None,
    stop_on_error: bool = False,
) -> list[ExtractionResult]:

    # 1. One result per config; a library error becomes a failed result
    results: list[ExtractionResult] = []
    for config in configs:
        try:
            results.append(extract(config, logger=logger))
        except SimpleException as exc:
            results.append(failure_result(config, exc))
            if stop_on_error:
                break

    return results
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `failure_result`

**Turns the error of a run that could not start into a result** — so a failed run still has a place in a list
of results.

**Parameters:**

| Name     | Type               | Description                          |
|----------|--------------------|--------------------------------------|
| `config` | `ExtractionConfig` | The config of the failed run.        |
| `error`  | `SimpleException`  | The error that stopped it.           |

**Returns:** an `ExtractionResult` with `fatal` set to a **one-line** description of the error, no files, no
output and `target=None`.

**Example usage:**

```python
from simplibs.exception import SimpleException
from simplibs.extractor import ExtractionConfig, extract
from simplibs.extractor.logic import failure_result

config = ExtractionConfig(source="no_such_folder")

try:
    result = extract(config)
except SimpleException as error:
    result = failure_result(config, error)

result.success                                          # -> False
result.fatal                                            # -> 'NotFoundError: ...'
result.files, result.target                             # -> ((), None)
result.profile_key                                      # -> 'generic/all'
```

**Which profile key.** The key as far as it is known **without resolving anything**: the key of a profile
object, a key as it was typed, or the default key if none was chosen. A typo in a key therefore shows up in the
report exactly as the person wrote it.

**Why a failed run is still a result.** `extract_many` runs several configs. If one of them is broken, the
others should still run and the report should still list all of them; a result with `fatal` is how the broken
one appears in that list.

<details>
<summary>🔍 Under the hood</summary>

```python
def failure_result(
    config: ExtractionConfig,
    error: SimpleException,
) -> ExtractionResult:

    # 1. The profile's key as far as it is known without resolving anything
    profile = config.profile
    if isinstance(profile, Profile):
        key = profile.key
    else:
        key = profile or DEFAULT_PROFILE_KEY

    # 2. Everything else stays at its empty default
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

### `process_source`

*Private helper.* **The body of the per-file loop** — reads one file and runs the profile's steps on it.

**Parameters:** `path` (`Path`, the absolute path of the file) and `plan` (`Resolved`).

**Returns:** a pair — the **final** `FileReport` of the file and its `Entry` (`None` unless the status is
`ok` or `partial`). A failure of this one file is reported, not raised.

It keeps `extract()` short and keeps the rule *"one bad file never stops the run"* in one place.

**The one broad `except` of the library.** Everywhere else only the cards and operating-system errors the code
knows are caught. Here the code is a profile's **step**, written by someone else, and may fail in any way;
reporting it against the file it failed on (`transform failed: …`) is the useful behaviour. A bug of this
library would surface in the other phases, not here.

**A warning makes a file partial.** A step that cannot handle a file fully returns the text as it got it and
warns (`warnings.warn`, a `UserWarning`). The warnings of the steps of one file are collected here: the file stays in
the output, its status is `partial` and the warning is its reason. A step that raises makes the file `error`, as
before. See [`transform`](README_EXTRACTOR_TRANSFORM.md) for the step's side of it.

**`bytes_out`** of the report is the size of the text **after** the steps, in UTF-8 bytes — what the file
contributes to the output, so the report shows what a profile saves.

<details>
<summary>🔍 Under the hood</summary>

```python
def process_source(
    path: Path,
    plan: Resolved,
) -> tuple[FileReport, Entry | None]:
    config, profile = plan.config, plan.profile

    # 1. Read; a skipped or failed file stops here
    report, text = read_source(path, config.source, config.max_file_size)
    if text is None:
        return report, None

    # 2. Transform; the steps are code from a profile, so any error of theirs belongs to this file.
    #    A step that cannot handle the file fully warns instead of failing; the warnings are collected here.
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        try:
            output = apply_steps(text, profile.steps, path.suffix)
        except Exception as exc:
            failed = dataclasses.replace(report, status="error", reason=f"transform failed: {describe_failure(exc)}")
            return failed, None

    # 3. A warning of a step means the file is in the output, but not fully processed
    reasons = _partial_reasons(caught)

    # 4. Included: remember how large the text is after the steps
    done = dataclasses.replace(
        report,
        status="partial" if reasons else "ok",
        reason="; ".join(reasons) or None,
        bytes_out=len(output.encode("utf-8")),
    )
    return done, Entry(done.relative, path.suffix.lower(), output)
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `RunLog`

*Private helper.* **A thin adapter that lets the run write progress to any logger, or to none.**

It accepts a `SimpleLogger` (`log_debug`, `log_info`, `log_success`, `log_warning`), a standard
`logging.Logger` (`debug`, `info`, `warning`; *success* is written as `info`), or `None`.

**Why an adapter and not an import.** `extract()` must not create a logger or print by itself, and it must
not force `simplibs-logger` on code that already has logging. Anything with the usual methods works. The
command passes a `SimpleLogger`, a script may pass nothing, an application may pass its own `Logger`.

**`%`-style arguments.** Messages are passed with their arguments, never pre-formatted, so a disabled level
costs no formatting.

<details>
<summary>🔍 Under the hood</summary>

```python
class RunLog:
    __slots__ = ("_logger",)

    def __init__(self, logger: Any = None) -> None:
        self._logger = logger

    def debug(self, message: str, *args: Any) -> None:
        self._emit("debug", "debug", message, args)

    def info(self, message: str, *args: Any) -> None:
        self._emit("info", "info", message, args)

    def success(self, message: str, *args: Any) -> None:
        self._emit("success", "info", message, args)

    def warning(self, message: str, *args: Any) -> None:
        self._emit("warning", "warning", message, args)

    def _emit(self, name: str, standard_name: str, message: str, args: tuple) -> None:

        # 1. No logger, no output
        if self._logger is None:
            return

        # 2. The simplibs method first, the standard `logging` method as the fallback
        method = getattr(self._logger, f"log_{name}", None) or getattr(self._logger, standard_name)
        method(message, *args)
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `build_title`

*Private helper.* **The heading of the output** — the one you configured, or a generated one.

**Parameters:** `config` (`ExtractionConfig`, resolved — its `source` is a normalized path).

**Returns:** `config.title` if it is set, otherwise `"Extraction: <name of the source folder>"`. A filesystem
root has no name, so its whole path is used.

```python
from pathlib import Path
from simplibs.extractor import ExtractionConfig
from simplibs.extractor.logic._helpers import build_title

source = Path("/home/me/my_project")  # a resolved config holds a normalized Path
build_title(ExtractionConfig(source=source))  # -> 'Extraction: my_project'
build_title(ExtractionConfig(source=source, title="My code"))  # -> 'My code'
```

Every output needs a title and most callers do not care what it is. Only the **name** of the folder is
written — never its absolute path (see [`RenderContext`](README_EXTRACTOR_RENDER.md#rendercontext)).

<details>
<summary>🔍 Under the hood</summary>

```python
def build_title(config: ExtractionConfig) -> str:

    # 1. A chosen title wins
    if config.title:
        return config.title

    # 2. The folder's name; a filesystem root has none, so its whole path is used
    return f"Extraction: {config.source.name or config.source}"
```

</details>

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../../README.md#-running-an-extraction)
