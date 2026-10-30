# 📊 `logic/report` — Phase 6: Say What Happened

The last phase turns what happened into something a person or a program can use. Its centre is the
[`ExtractionResult`](../README_EXTRACTOR_DEFINITIONS.md#extractionresult) — per-file reports, sizes, a rough
token count, a verdict — which `extract()` builds at the end of every run. This package holds the two helpers
that make that result useful: one **estimates the size** of the output in tokens, the other **writes the
result as readable text**.

```
ExtractionResult ──► format_summary ──► a few readable lines
      ▲                                  (the command prints them, a script logs them, a test compares them)
      │
estimate_tokens(rendered)  ──►  result.tokens_estimate
```

**Nothing in a run prints.** The run builds a result; the command, a script or your own code decide what to
do with it. The summary is a function *of the result*, so it can be printed, logged, written to a file or
compared in a test — and it is the same text in all of those places.

```python
from simplibs.extractor import estimate_tokens, extract, format_summary

result = extract(source="my_project")
print(format_summary(result))
```

```text
Extraction: generic/all
  source : /home/me/my_project
  target : /home/me/my_project/extraction.md (written)
  files  : 4 ok, 1 skipped, 0 errors
  size   : 133 B in -> 502 B out (~115 tokens)
  skipped: logo.png (not a text file)
```

```python
estimate_tokens("hello world")                          # -> 3
```

## What is public

Both functions are exported from the package root and validated with `@validate_call`: a wrong type is
refused with a `ValidationError` before the body runs.

---

## 🧭 Table of Contents

* [`estimate_tokens`](#estimate_tokens)
* [`format_summary`](#format_summary)

[⬅️ Back to main README](../../README.md#-the-six-phases)

---

### `estimate_tokens`

**Estimates how many tokens a language model would count in a text** — a rough number, not a count.

**Parameters:**

| Name              | Type    | Default | Description                                                              |
|-------------------|---------|---------|--------------------------------------------------------------------------|
| `text`            | `str`   |         | The text.                                                                |
| `chars_per_token` | `float` | `4.0`   | The assumed average number of **characters** per token.                  |

**Returns:** the estimated number of tokens as an `int` (`0` for an empty text). A started token is a token:
the result is rounded **up**.

**Raises:**
`ParamError` (`EXTRACTOR_CONFIG_INVALID`) — `chars_per_token` is zero or negative.
`ValidationError` — `text` is not a string, or `chars_per_token` is not a number.

**Example usage:**

```python
from simplibs.extractor import estimate_tokens

estimate_tokens("hello world")                          # -> 3        11 characters / 4, rounded up
estimate_tokens("a" * 400)                              # -> 100
estimate_tokens("")                                     # -> 0

# non-Latin text and some languages need a lower ratio — that is why it is a parameter
estimate_tokens("příliš žluťoučký kůň")                 # -> 5        20 characters / 4
estimate_tokens("příliš žluťoučký kůň", chars_per_token=2.5)    # -> 8

estimate_tokens("x", chars_per_token=0)                 # raises ParamError — must be greater than zero
estimate_tokens(5)                                      # raises ValidationError — not a string
```

**Characters, not bytes.** The estimate counts the characters of the text. The box-drawing characters of a tree
take three bytes each in UTF-8 but are one character each, which is why a result can show `502 B out` and
`~115 tokens`.

**Where the library uses it.** `ExtractionResult.tokens_estimate` is the estimate of the **whole rendered
output** — title, tree and fences included — with the default ratio. It answers the first question one asks
about an output: *"will this fit into a context window?"*

**Why an estimate and not a count.** Any exact count would need a particular tokenizer and would age with the
models. The function says *estimate* in its name and does not pretend: about four characters per token is
close enough for code and English, and the parameter lets you correct it for other text. There is no model
name and no tokenizer anywhere in the library.

<details>
<summary>🔍 Under the hood</summary>

```python
@validate_call
def estimate_tokens(
    text: str,
    chars_per_token: float = 4.0,
) -> int:

    # 1. A zero or negative ratio would divide by zero or return nonsense
    if chars_per_token <= 0:
        raise_chars_per_token_error(chars_per_token)

    # 2. Round up: a started token is a token
    return math.ceil(len(text) / chars_per_token)
```

`extract()` applies it to the rendered output:

```python
tokens_estimate=estimate_tokens(rendered)
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `format_summary`

**Describes the outcome of one extraction as readable text** — what was extracted, where it went, the counts
and sizes, and the files that need attention, **errors first**.

**Parameters:**

| Name         | Type               | Default | Description                                                                 |
|--------------|--------------------|---------|-----------------------------------------------------------------------------|
| `result`     | `ExtractionResult` |         | The result of `extract()`.                                                  |
| `max_listed` | `int`              | `10`    | How many failed and skipped files are listed by name. *(keyword-only)*      |

**Returns:** a `str` of a few lines, without a trailing line ending.

**Raises:** `ValidationError` — `result` is not an `ExtractionResult`, or `max_listed` is not an integer.

**The layout.**

| Line      | What it says                                                                                          |
|-----------|-------------------------------------------------------------------------------------------------------|
| 1         | `Extraction: <profile key>`                                                                           |
| `source`  | the source folder                                                                                     |
| `target`  | the output path and its state: `written`, `not written`, or `dry run, not written`                    |
| `files`   | how many files are `ok`, `skipped` and `error`                                                        |
| `size`    | the bytes in, the bytes out and the token estimate, with thousands separators                         |
| the rest  | one line per failed file, then one per skipped file — `status: path (reason)`; at most `max_listed` lines in all |
| last      | a hint, only if no file was extracted: `nothing to extract (check the source and the include/exclude rules)` |

**Example usage:**

```python
from simplibs.extractor import extract, format_summary

# 1. A normal run
print(format_summary(extract(source="my_project")))
```

```text
Extraction: generic/all
  source : /home/me/my_project
  target : /home/me/my_project/extraction.md (written)
  files  : 4 ok, 1 skipped, 0 errors
  size   : 133 B in -> 502 B out (~115 tokens)
  skipped: logo.png (not a text file)
```

```python
# 2. A dry run says so, and nothing was written
print(format_summary(extract(source="my_project", dry_run=True)))
#   target : /home/me/my_project/extraction.md (dry run, not written)
```

```python
# 3. A failed file comes before the skipped ones
print(format_summary(result))
```

```text
Extraction: python/code-clean
  source : /home/me/my_project
  target : /home/me/my_project/python_clean.md (written)
  files  : 2 ok, 1 skipped, 1 errors
  size   : 72 B in -> 300 B out (~75 tokens)
  error  : src/broken.py (transform failed: OperationError: ...)
  skipped: logo.png (not a text file)
```

```python
# 4. A run that never started has one thing to say
results = extract_many([ExtractionConfig(source="no_such_folder")])
print(format_summary(results[0]))
```

```text
Extraction: generic/all
  FAILED: NotFoundError: ...
```

```python
# 5. Nothing selected: the most common mistake has its own hint
print(format_summary(extract(source="empty_folder")))
```

```text
Extraction: generic/all
  source : /home/me/empty_folder
  target : /home/me/empty_folder/extraction.md (not written)
  files  : 0 ok, 0 skipped, 0 errors
  size   : 0 B in -> 0 B out (~0 tokens)
  nothing to extract (check the source and the include/exclude rules)
```

```python
# 6. Only the first lines of problems are listed — the counts above them stay complete
format_summary(result, max_listed=3)                    # at most three failed or skipped files are named
format_summary(result, max_listed=0)                    # the counts only
```

**Errors first.** A failed file is what a reader is looking for. Failed files are listed before skipped ones,
and the cap `max_listed` applies to both together — so a long list of skipped files can never push an error out
of view. The counts on the `files` line are always complete.

**No colors.** The summary is plain text. The command decides how to color it; the function stays usable in
logs and files.

**Why it is a function of the result.** The command prints it, a script can log it and a test can compare it.
Nothing in the run prints on its own — everything goes through the result.

<details>
<summary>🔍 Under the hood</summary>

```python
@validate_call
def format_summary(
    result: ExtractionResult,
    *,
    max_listed: int = 10,
) -> str:

    # 1. A run that stopped early has one thing to say
    lines = [f"Extraction: {result.profile_key}"]
    if result.fatal:
        return "\n".join(lines + [f"  FAILED: {result.fatal}"])

    # 2. What happened to the output
    if result.dry_run:
        state = "dry run, not written"
    else:
        state = "written" if result.written else "not written"

    # 3. The facts
    lines += [
        f"  source : {result.config.source}",
        f"  target : {result.target} ({state})",
        f"  files  : {len(result.ok_files)} ok, {len(result.skipped_files)} skipped, {len(result.error_files)} errors",
        f"  size   : {result.bytes_in:,} B in -> {result.bytes_out:,} B out (~{result.tokens_estimate:,} tokens)",
    ]

    # 4. Files that need a look: errors before skipped ones, capped
    for report in (*result.error_files, *result.skipped_files)[:max_listed]:
        lines.append(f"  {report.status:<7}: {report.relative} ({report.reason})")

    # 5. The most common mistake deserves its own hint
    if not result.ok_files:
        lines.append("  nothing to extract (check the source and the include/exclude rules)")

    return "\n".join(lines)
```

</details>

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../../README.md#-the-six-phases)
