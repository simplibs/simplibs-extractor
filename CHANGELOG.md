# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

---

## [0.2.0] - 2026-11-02

### ✨ Added

#### Profiles — helpers for add-ons

* `by_suffix(step, suffixes)` — gives one step to every suffix of a list and returns the mapping `suffix -> step` that `Profile.steps` takes; every add-on wrote the same three lines before. Exported from `simplibs.extractor` and `simplibs.extractor.logic`

#### Code-fence languages — a registry

* `register_language(suffix, language, *, replace_existing=False)` — adds the language the Markdown output writes after the fence of a file suffix (`".lua"` → `"lua"`); a taken suffix needs `replace_existing=True`; a suffix that is not lowercase with a dot, and a name with whitespace or a backtick, are refused
* `get_language(suffix)` — the language of a suffix (the case is ignored), or `None` if nobody registered it
* `list_languages()` — the registered languages sorted by suffix, as a new dictionary
* `.mjs` and `.cjs` in the built-in table `LANGUAGE_BY_SUFFIX`; the registry starts as a copy of it and the table itself stays read-only
* The Markdown renderer asks the registry, so the languages that add-ons register are highlighted too

#### A file that was processed only partly

* New file status `"partial"` — the file is in the output, but a step could not process it fully (a Python source that does not parse, say). A step that cannot handle a file returns the text as it got it and warns (`warnings.warn(...)`, a `UserWarning`); the extractor collects the warnings of the steps of one file and reports the file as `partial`, with the text of the warning as the reason. Other warning categories (`DeprecationWarning`, ...) are not counted; a step that raises still makes the file `error`
* `ExtractionResult.partial_files`; `success` counts a partial file as a file in the output, so a run that has only partial files is successful
* `format_summary` shows `partial` in the counts only when there is such a file, and lists partial files between the failed and the skipped ones
* The run logs a partial file as a warning

#### Testing — tools for the add-ons

* `simplibs.extractor.testing` — a new package for testing the profiles of an add-on; the package root does not import it, and it needs `pytest` 9 or newer (the report is built from the native `subtests` fixture; `pip install simplibs-extractor[dev]`)
* `assert_profile(subtests, profile, ...)` — checks everything a profile promises in one call, with a subtest for each thing it checks, so one run shows everything that is wrong with a profile: the key and a one-line description, the output name and format, which relative paths the `include` and `exclude` rules take and leave out, and what the steps do to a text, suffix by suffix
* The three blades behind it, which can also be called alone from `simplibs.extractor.testing.asserts`: `assert_profile_identity`, `assert_profile_selection` and `assert_profile_steps`; a blade runs only when there is data for it
* A mistake of the test itself (a path in both lists, a suffix that no file can have, a first argument that is not a `Profile`) is an `AssertionError` raised at once, before any subtest; the tools define no exceptions of their own and raise no cards
* `testing` is the last layer of the package (`... ← scripts ← cli ← testing`): it may look at everything and nothing looks at it

### 🔄 Changed

* `FileStatus` has a fourth value; code that handles the three old ones with an exhaustive `match` needs a branch for `"partial"`
* The size of a partial file counts in `ExtractionResult.bytes_in`, like the size of an `ok` file

### 📚 Documentation

* `README_EXTRACTOR_TRANSFORM` (`by_suffix`, a step that warns), `README_EXTRACTOR_REGISTRY` (languages), `README_EXTRACTOR_CONSTANTS`, `README_EXTRACTOR_ANNOTATIONS`, `README_EXTRACTOR_DEFINITIONS`, `README_EXTRACTOR_REPORT`, `README_EXTRACTOR_RUN` and the main `README`
* `README_EXTRACTOR_PLUGINS`: recommendations for the profiles of an add-on
* `README_EXTRACTOR_TESTING` (new): `assert_profile` and its three blades, and a `testing` section in the main `README`

---

## [0.1.1] - 2026-10-31

### 🐛 Fixed

* `extract_here(...)` and `generate_local_script(...)` now load the installed add-ons (`load_plugins()`) before they look up a profile **given as a key**; before, a profile of an add-on (`python/code-clean`) was never registered in a fresh process, so a generated script, a direct call and `simplibs-extractor init --profile …` failed with `EXTRACTOR_PROFILE_NOT_FOUND` even with the add-on installed
* A `Profile` object or no profile (`generic/all`) does not trigger the lookup; calling it repeatedly is safe because add-ons register with `replace_existing=True`
* `extract()` is unchanged: it still never loads add-ons on its own

### 📋 Improved

* Documentation of `extract_here`, `generate_local_script` and add-on loading (`README`, `README_EXTRACTOR_SCRIPTS`, `README_EXTRACTOR_PLUGINS`)

---

## [0.1.0] - 2026-10-30

### ✨ Added

#### Running an extraction

* `extract(config=None, *, logger=None, **overrides)` — one extraction through all six phases; takes a ready `ExtractionConfig`, plain keyword values, or both (the keywords then change a copy of the config); an unknown keyword is refused with a card that lists the valid names; nothing is printed, progress goes to the `logger`
* `extract_many(configs, *, logger=None, stop_on_error=False)` — several extractions in a row; a run that cannot start or cannot write is a result with `fatal` set and does not stop the others
* `extract_here(anchor, profile=None, *, output_name=None, quiet=False, logger=None, **overrides)` — extracts the folder of a script into a file next to it; the script itself is never part of the output; derived values lose to the caller's own, except `skip_paths`, which is extended; the one library function that prints, unless `quiet=True`
* `generate_local_script(path, profile=None, *, overwrite=False)` — writes a ready-to-run `extract_here.py` (a folder gets `extract_here.py`); only the profile's key is stored; an existing script is not replaced unless asked

#### The six phases

* **Select** — scans the folder (`recursive`, `ignore_names`; the default is the housekeeping names of `simplibs-path` plus the draft files of `SafeFileWriter`), removes the target and `skip_paths`, and applies the rules of the profile and of the config to the path **relative to the source**: `include` combined by AND, `exclude` by OR, so a config only narrows a profile
* **Read** — per file, cheapest check first: binary → generated by this library → too large → read; reports `skipped` or `error` and never raises for the file's own problems
* **Transform** — runs the profile's steps on the text: one `Action` for every file, or the action of the file's suffix (`"*"` is the fallback); a step must return a `str`; a step that fails marks only that file as `error` and the run continues
* **Render** — one text through the renderer of the format, with a title, an optional directory tree and the generated marker; only the name of the source folder is written, never its absolute path
* **Write** — `overwrite` (atomic), `unique`, `backup` or `error`; a dry run makes the same decisions, including the refusal of an existing output under `error`, and writes nothing; the folder of the output is created when missing
* **Report** — an `ExtractionResult` with per-file reports, sizes and a rough token estimate; an extraction that selected nothing (or whose every file failed) writes nothing and is unsuccessful
* Default limit of one megabyte per file; larger files are skipped with their reason, not dropped silently

#### Profiles and the registry

* `Profile(system, name, description="", include=None, exclude=None, steps=None, output_name="extraction.md", format="markdown")` — a named set of selection rules and steps, frozen and validated when built; `key` is `"system/name"`
* `register_profile(profile, *, replace_existing=False)` — adds a profile under its key and returns it
* `get_profile(key)`, `list_profiles(system=None)`, `list_systems()` — lookups; a missing key is a card that lists the registered ones; listings are sorted and detached from the registry
* `expand_profile_keys(system, names)` — turns typed names into full keys (`("python", "a,b")` → `["python/a", "python/b"]`); a full key is kept as it is
* `generic/all` — the built-in profile (every text file, unchanged), registered on import, so the extractor is useful without any add-on

#### Add-ons

* `load_plugins(*, group="simplibs.extractor.plugins", entry_points=None)` — lets every installed add-on register its profiles through an entry point; returns `(loaded, failed)` and a failing add-on never stops the others; safe to call twice; the command calls it itself, from Python it is called once by the program (`extract()` never loads add-ons on its own)
* `PLUGIN_GROUP` — the entry-point group in which add-on packages announce themselves

#### Output formats

* `register_renderer(name, func, *, replace_existing=False)`, `get_renderer(name)`, `list_formats()` — formats are registered by name; a renderer is a function `(entries, context) -> str`
* `markdown` (default) — a marker comment, a title, the profile, an optional tree, and a heading with a fenced code block per file; the fence is always longer than any run of backticks inside the code, an empty file is noted, the language comes from the suffix (`LANGUAGE_BY_SUFFIX`)
* `plain` — the layout of the old code extractor: a header, an optional `# TREE` and `# FILE: path` blocks
* `RenderContext(title, source, profile_key, add_tree)` — what a renderer knows besides the entries
* `build_tree(paths)` — draws a directory tree from relative paths, folders first (`simplibs.extractor.logic`)
* Every built-in output carries `GENERATED_MARKER` in its first lines, so an earlier output (also `extraction (1).md` or a backup) is recognised and skipped

#### Reporting

* `ExtractionResult` — `config`, `profile_key`, `target`, `written`, `dry_run`, `files`, `bytes_in`, `bytes_out`, `tokens_estimate`, `duration`, `fatal`, and the properties `ok_files`, `skipped_files`, `error_files` and `success`
* `FileReport` — `path`, `relative`, `status`, `reason`, `bytes_in`, `bytes_out`; a skipped or failed file keeps its reason
* `Entry(relative, suffix, text)` — one file ready to be rendered
* `format_summary(result, *, max_listed=10)` — a readable summary, errors first
* `estimate_tokens(text, chars_per_token=4.0)` — a rough token count; no model name, no tokenizer

#### Configuration

* `ExtractionConfig(source, target=None, profile=None, include=None, exclude=None, ignore_names=None, recursive=True, format=None, overwrite="overwrite", dry_run=False, max_file_size=1_000_000, add_tree=True, title=None, skip_paths=())` — everything one run needs; frozen and validated; `include` and `exclude` are single `Rule` objects (compose them with `&`, `|` and `~`), never lists
* `OverwritePolicy` — `"overwrite"`, `"unique"`, `"backup"` or `"error"`
* `OutputFormat` — the name of a format (lowercase, starts with a letter); whether a renderer exists is checked when the configuration is resolved
* `StepsSpec` — `None`, one `Action`, or a mapping `suffix -> Action`
* `FileStatus` — `"ok"`, `"skipped"` or `"error"`
* Constants: `DEFAULT_PROFILE_KEY` and `GENERATED_MARKER` (also from the package root), `DEFAULT_MAX_FILE_SIZE`, `DEFAULT_OUTPUT_NAME`, `DEFAULT_SCRIPT_NAME`, `LANGUAGE_BY_SUFFIX`, `MARKER_SCAN_LINES`, `PLUGIN_GROUP` and `SCRIPT_TEMPLATE` (all in `simplibs.extractor.constants`)

#### Command line

* `simplibs-extractor [SYSTEM] [PROFILES] [SOURCE]` with `-o/--output`, `--format`, `--overwrite`, `--no-tree`, `--dry-run`, `-q/--quiet`, `-v/--verbose` (counted, `-vv`), `--no-color`, `--list-systems` and `--list-profiles SYSTEM`; also `python -m simplibs.extractor`
* `simplibs-extractor init [DIRECTORY] [--profile KEY] [--force]` — writes a local `extract_here.py`
* Several profiles in one run (`code-clean,data-all`) are several extractions and several files; everything that can be refused — a mistyped key, a file given as the output folder, two profiles that would write the same file — is checked before the first extraction runs
* A first word that is a folder and not a registered system or key is taken as the source
* Missing values are asked for in a terminal (system, profiles, source; a dry-run question only to a person who is already being asked); without a terminal the same situation is a card, never a hang
* Exit codes: `0` everything succeeded, `1` some extraction failed or selected nothing, `2` the command was refused before anything ran
* Installed add-ons are loaded before the parser is built, and one that fails to load is a warning, not a stop
* The command line is not imported by the package root, so a program that only calls `extract()` does not load the prompt and logger libraries

#### Exceptions

* The library defines no exceptions of its own; a wrong call raises a card of `simplibs-exception`
* The functions that raise the cards are private: each lives in a `_validations/` folder next to the code that uses it
* Error names: `EXTRACTOR_CONFIG_INVALID`, `EXTRACTOR_PROFILE_EXISTS`, `EXTRACTOR_PROFILE_INVALID`, `EXTRACTOR_PROFILE_NOT_FOUND`, `EXTRACTOR_SOURCE_NOT_FOUND`, `EXTRACTOR_STEP_RESULT_INVALID`, `EXTRACTOR_TARGET_EXISTS`, `EXTRACTOR_TARGET_IS_DIR`

#### Typing

* `py.typed` marker — the package ships its type information (declared in `package-data`, so it is part of the built wheel)

#### Package Layout

* `simplibs.extractor` exports everything a program needs; the command line is `simplibs.extractor.cli`
* `simplibs.extractor.logic` declares its own surface in an `__all__`: the six phases and the run, for programs that build a pipeline of their own
* Layers that only look left: `annotations` ← `constants` ← `definitions` ← `registry` ← `logic` ← `plugins` ← `scripts` ← `cli`
* Importing the package registers the profile `generic/all` and the formats `markdown` and `plain`; nothing else happens until a function is called

#### Documentation

* Main `README.md` with a quick start in four levels, the six phases, the package structure, a quick reference, the command line, the table of error names and an index of the detailed references
* Detailed references in `docs/`: `README_EXTRACTOR_ANNOTATIONS`, `README_EXTRACTOR_CONSTANTS`, `README_EXTRACTOR_DEFINITIONS`, `README_EXTRACTOR_REGISTRY`, `README_EXTRACTOR_PLUGINS`, `README_EXTRACTOR_SCRIPTS` and `README_EXTRACTOR_CLI`, and under `docs/logic/` one for each phase — `README_EXTRACTOR_RUN`, `_SELECT`, `_READ`, `_TRANSFORM`, `_RENDER`, `_WRITE` and `_REPORT`

#### Dependencies

* `simplibs-exception` — the structured cards behind every error
* `simplibs-validate` — `@validate_call` on the public functions and `@validate_dataclass` on `ExtractionConfig` and `Profile`
* `simplibs-path` — scanning, normalized and relative paths, unique names
* `simplibs-file` — reading, the text check, the size, the atomic write and the backup
* `simplibs-rules` — the `Rule` objects behind `include` and `exclude`
* `simplibs-actions` — the `Action` objects a profile's steps are made of
* `simplibs-markdown` — the Markdown output
* `simplibs-cli` — the prompts, the failure summary and the verbosity of the command
* `simplibs-logger` — the logger the command passes to the run
* `simplibs-style` — the colors of the command, which switch themselves off outside a terminal

---

## Legend

* 🔄 **Changed** — modifications to existing functionality
* ✨ **Added** — new features and components
* 🐛 **Fixed** — bug fixes
* 📋 **Improved** — enhancements to existing features
* ⚠️ **Deprecated** — deprecated functionality (not used yet in this project)
* 🗑️ **Removed** — removed functionality (not used yet in this project)
