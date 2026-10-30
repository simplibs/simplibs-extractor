# ⌨️ `cli` — The Command Line

The `cli` package is the **command** `simplibs-extractor`: the same extraction as `extract()`, for a person at
a terminal or a CI job. It turns *words* into configurations, asks for what is missing, runs everything and
turns the outcome into an **exit code**.

```
simplibs-extractor [SYSTEM] [PROFILES] [SOURCE] [-o FOLDER] [--format NAME] [--overwrite POLICY]
                   [--no-tree] [--dry-run] [-q] [-v | -vv] [--no-color]
simplibs-extractor --list-systems | --list-profiles SYSTEM
simplibs-extractor init [DIRECTORY] [--profile KEY] [--force]
```

```text
simplibs-extractor python code-clean ./my_project              # one profile
simplibs-extractor python code-clean,data-all ./my_project     # two profiles: two extractions, two files
simplibs-extractor generic/all,python/data-all ./my_project    # full keys, from different systems
simplibs-extractor ./my_project                                # only the folder: the profiles are asked
simplibs-extractor                                             # nothing: system, profiles and folder are asked
```

The command is also reachable as `python -m simplibs.extractor`.

## The command is a thin layer

Everything the command does is one of these steps, and each step is a function of this package:

```
words ──► build_parser ──► normalize_positionals ──► handle_list_options  (--list-*: answer and stop)
                                   │
                                   ▼
        collect_profile_keys · collect_source · collect_dry_run     ask for what is missing
                                   │
                                   ▼
                             build_configs        one ExtractionConfig per profile, every refusal checked HERE
                                   │
                                   ▼
                      extract_many  ──►  summaries  ──►  failures once more  ──►  exit code
```

Order matters: **add-ons are loaded first** (their profiles and formats belong in the parser's choices), then
the parser is built, then the questions are asked, then **everything that can be refused is checked — before
the first extraction runs**. A typo in the second profile must not cost the first profile's output.

The command line is **not imported by the package root**: a program that only calls `extract()` does not load
the prompt, logger and style libraries.

## Options

| Option                       | Meaning                                                                                                       |
|------------------------------|---------------------------------------------------------------------------------------------------------------|
| `SYSTEM PROFILES`            | `python code-clean,data-all`, or full keys: `python/code-clean`, `generic/all,python/data-all`. Several profiles are several runs and several files. |
| `SOURCE`                     | The folder to extract from.                                                                                   |
| `-o`, `--output FOLDER`      | The output **folder** (default: the source). The file name always comes from the profile.                     |
| `--format NAME`              | An output format; the choices are the registered ones. Default: the profile's.                                |
| `--overwrite POLICY`         | `overwrite` (default), `unique`, `backup` or `error` — the values of [`OverwritePolicy`](README_EXTRACTOR_ANNOTATIONS.md#overwritepolicy). |
| `--no-tree`                  | Leave the directory tree out of the output.                                                                   |
| `--dry-run`                  | Plan and report, write nothing.                                                                               |
| `-q`, `--quiet`              | Only errors; the per-run summaries are not printed.                                                           |
| `-v`, `-vv`                  | More detail / everything (the progress messages of the run).                                                  |
| `--no-color`                 | Plain text, no colors.                                                                                        |
| `--list-systems`             | List the registered systems and exit.                                                                         |
| `--list-profiles SYSTEM`     | List the profiles of one system and exit. An unknown system is an error, not an empty list.                   |
| `init`                       | Write a local `extract_here.py` (see [`run_init`](#run_init)).                                                |

## How the three words are read

`argparse` fills the three positionals strictly in order, but people type `simplibs-extractor ./src` or
`simplibs-extractor generic/all ./src`. The command sorts them out **by the registry first and by the disk
second**:

| You type                                      | Read as                                                                                  |
|-----------------------------------------------|------------------------------------------------------------------------------------------|
| `python code-clean ./src`                     | system, profiles, source                                                                 |
| `python`                                      | a system; the profiles and the source are asked                                          |
| `generic/all ./src`, `a/b,c/d ./src`          | full keys, then the source — a word with `/` or `,` is a list of profiles                |
| `./src` (a folder that is **not** a registered system or key) | the source; the profiles are asked                                       |
| `python` when a folder `python` exists        | still the **system** — a registered system or key always wins over a folder of the same name |
| `generic/all a b`                             | **refused** — full keys followed by two more words                                       |

## What is asked, and what happens without a terminal

What is missing is asked for **in a terminal**: the system, then the profiles, then the source. A dry-run
question is asked **only to a person who is already being asked** — someone who typed the complete command wants
it to run, not another question.

Without a terminal the same situation is a **card** that names the missing argument — a CI job never hangs.

## Exit codes and output

| Exit code | Meaning                                                                                              |
|:---------:|------------------------------------------------------------------------------------------------------|
| `0`       | Everything succeeded.                                                                                |
| `1`       | Some extraction failed, a file failed, or nothing was selected.                                      |
| `2`       | The command was refused before anything ran: a mistyped profile, a missing source with nobody to ask, two profiles that would write the same file. |

`--help` and syntax errors of the arguments (an unknown option, a `--format` that is not registered) exit
through `argparse`.

Summaries go to **standard output**, refusals to **standard error** — so a piped result never mixes with
diagnostics — and progress goes through a logger at the level `-q`, `-v` and `-vv` choose. A failing add-on is
a **warning**, not a stop.

## What is public

The entry point is `run_cli`, declared as the console script
`simplibs-extractor = simplibs.extractor.cli:run_cli`; it **returns** the exit code, which the console script
passes to `sys.exit`. The other functions are importable from `simplibs.extractor.cli` and are documented here
for readers who want to know exactly how the words are read, and for tests.

---

## 🧭 Table of Contents

**The command**

* [`run_cli`](#run_cli)
* [`run_init`](#run_init)

**Reading the words**

* [`build_parser`](#build_parser)
* [`normalize_positionals`](#normalize_positionals)

**Collecting what is missing**

* [`collect_profile_keys`](#collect_profile_keys)
* [`collect_source`](#collect_source)
* [`collect_dry_run`](#collect_dry_run)

**From words to configurations**

* [`build_configs`](#build_configs)
* [`handle_list_options`](#handle_list_options)

**Private helpers**

* [`describe_result`](#describe_result), [`is_profile_reference`](#is_profile_reference),
  [`print_error`](#print_error), [`profile_options`](#profile_options), [`system_options`](#system_options)

[⬅️ Back to main README](../README.md#-the-command-line)

---

### `run_cli`

**The `simplibs-extractor` command**, start to finish. Everything a person types ends here and comes out as an
exit code that scripts and CI can read.

**Parameters:**

| Name   | Type                        | Default | Description                                                                   |
|--------|-----------------------------|---------|-------------------------------------------------------------------------------|
| `argv` | `Sequence[str] \| None`     | `None`  | The arguments **without** the program name; `None` reads `sys.argv`.          |

**Returns:** the exit code as an `int` — `0` everything succeeded, `1` some extraction failed or selected
nothing, `2` the command was refused before anything ran.

**Raises:** nothing for a refused command — it is printed to standard error and becomes exit code `2`. Only
`SimpleError` (the cards of this library and of `simplibs-cli`) is turned into a refusal; a bug keeps its
traceback, and `Ctrl+C` is not caught.

**Example usage:**

```python
from simplibs.extractor.cli import run_cli

run_cli(["generic/all", "my_project"])                          # -> 0     summary printed, my_project/extraction.md written
run_cli(["generic/all", "my_project", "--dry-run", "--no-tree"])   # -> 0  planned, nothing written
run_cli(["generic/all", "empty_folder"])                        # -> 1     nothing was selected
run_cli(["python/nope", "my_project"])                          # -> 2     the card goes to standard error
run_cli(["generic/all,generic/all", "my_project"])              # -> 2     two profiles would write the same file
run_cli(["--list-systems"])                                     # -> 0     the systems printed, nothing extracted
run_cli(["init", "my_project"])                                 # -> 0     the subcommand, see run_init
```

A console script passes the code on: `sys.exit(run_cli())`.

**The order, in short.**

| Step | What happens                                                                                                  |
|-----:|---------------------------------------------------------------------------------------------------------------|
| 1    | Installed add-ons are loaded ([`load_plugins`](README_EXTRACTOR_PLUGINS.md)).                                 |
| 2    | `init` has its own parser and goes to [`run_init`](#run_init) — after the add-ons, because its profile choice lists their profiles. |
| 3    | The arguments are parsed and the three words sorted; `--no-color` and the logger level are applied; a failing add-on becomes a warning. |
| 4    | `--list-systems` / `--list-profiles` answer from the registry and end the command.                            |
| 5    | Profiles, source and the dry-run flag are collected; one configuration per profile is built. Every refusal happens here. |
| 6    | `extract_many` runs them all. A failed one is a result, not an exception; each summary is printed unless `-q`. |
| 7    | The failures are reported once more, together, and the exit code is chosen.                                   |

**Why exit code `2` for "refused".** Scripts and CI can tell *"the command was wrong"* (2) from *"it ran and
something failed"* (1) — a typo in a profile is a different kind of problem from a file that could not be read.

**Why the failures are listed again.** With several profiles the summaries scroll by; the closing report
names every run that did not succeed, one line each, so a long output cannot hide it.

<details>
<summary>🔍 Under the hood</summary>

```python
def run_cli(argv: Sequence[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)

    # 1. Installed add-ons first: their profiles and formats belong in the parser's choices
    loaded, failed = load_plugins()

    # 2. A subcommand has its own parser
    if arguments[:1] == ["init"]:
        return run_init(arguments[1:])

    # 3. Parse, then sort the positional words into their roles
    args = normalize_positionals(build_parser().parse_args(arguments))
    if args.no_color:
        set_styles_enabled(False)
    logger = SimpleLogger(name="extractor", level=resolve_verbosity(quiet=args.quiet, verbose=args.verbose))
    for name, reason in failed.items():
        logger.log_warning("The add-on '%s' did not load: %s", name, reason)

    try:
        # 4. Questions about the registry end the command here
        if handle_list_options(args):
            return 0

        # 5. Everything that can be refused is checked before the first extraction runs
        asked = not args.profiles or args.source is None
        keys = collect_profile_keys(args)
        source = collect_source(args)
        configs = build_configs(args, keys, source, collect_dry_run(args, asked))
    except SimpleError as exc:
        print_error(exc)
        return 2

    # 6. Run all of them; a failed one is a result, not an exception
    results = extract_many(configs, logger=logger)
    if not args.quiet:
        for result in results:
            print_result(result)

    # 7. The failures once more, together, and the exit code
    everything_ok = report_failures(
        [(result, result.success) for result in results],
        describe=describe_result,
    )
    return 0 if everything_ok else 1
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `run_init`

**The `init` command: writes a local `extract_here.py` script** into a folder, so from then on the extraction
is `python extract_here.py`.

**Parameters:**

| Name   | Type            | Description                                                         |
|--------|-----------------|---------------------------------------------------------------------|
| `argv` | `Sequence[str]` | The arguments **after** the word `init`.                            |

Its own small parser takes `directory` (default: the current folder), `--profile KEY` and `--force`.

**Returns:** the exit code — `0` if the script was written, `2` if the command was refused.

**Example usage:**

```python
from simplibs.extractor.cli import run_init

run_init(["my_project", "--profile", "python/code-clean"])      # -> 0
# Created: /home/me/my_project/extract_here.py
# Run it with:  python extract_here.py

run_init(["my_project", "--profile", "python/code-clean"])      # -> 2     the script exists; the card goes to standard error
run_init(["my_project", "--profile", "python/code-clean", "--force"])       # -> 0     replaced, as asked
run_init(["my_project", "--profile", "python/nope"])            # -> 2     unknown profile; nothing is written
run_init(["my_project"])                                        # in a terminal: the profile is asked; elsewhere: generic/all
```

The same from the shell: `simplibs-extractor init my_project --profile python/code-clean`.

**No terminal, no question.** Without a profile and without a terminal the script gets `generic/all` — a pipe
or a CI job must not hang on a question. In a terminal the choice lists the registered profiles with
`generic/all` preselected.

**An existing script is refused unless `--force`.** It may have been edited. The card is the one
`simplibs-file` raises; the details are in
[`generate_local_script`](README_EXTRACTOR_SCRIPTS.md#generate_local_script).

<details>
<summary>🔍 Under the hood</summary>

```python
def run_init(argv: Sequence[str]) -> int:

    # 1. The command's own small parser
    parser = argparse.ArgumentParser(prog="simplibs-extractor init", description="Write a local extraction script.")
    parser.add_argument("directory", nargs="?", type=Path, default=Path("."), help="the folder for the script (default: here)")
    parser.add_argument("--profile", help="the profile key the script uses (default: asked, or generic/all)")
    parser.add_argument("--force", action="store_true", help="replace an existing script")
    args = parser.parse_args(list(argv))

    # 2. No profile given: a terminal is asked, anything else gets the default
    profile = args.profile
    if profile is None and is_interactive():
        options = {item.key: item.description for item in list_profiles()}
        profile = prompt_choice("Profile", options, default=DEFAULT_PROFILE_KEY)

    # 3. Write the script; every refusal of the library is a card
    try:
        created = generate_local_script(args.directory, profile, overwrite=args.force)
    except SimpleError as exc:
        print_error(exc)
        return 2

    # 4. Say what to do next
    print(SUCCESS(f"Created: {created}"))
    print(f"Run it with:  {Path(sys.executable).name} {created.name}")
    return 0
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `build_parser`

**Builds the argument parser of `simplibs-extractor`** — the whole syntax of the tool, read here and nowhere
else.

**Parameters:** none.

**Returns:** an `argparse.ArgumentParser`. Every positional argument is optional: what is missing is asked
for, or refused when there is nobody to ask.

**Example usage:**

```python
from simplibs.extractor.cli import build_parser

parser = build_parser()

args = parser.parse_args(["python", "code-clean", "my_project", "--dry-run"])
args.system, args.profiles, args.source                 # -> ('python', 'code-clean', Path('my_project'))
args.dry_run                                            # -> True

args = parser.parse_args([])
args.dry_run                                            # -> None     "not given" is different from "no"
args.overwrite, args.add_tree, args.verbose             # -> ('overwrite', True, 0)

parser.parse_args(["-vv"]).verbose                      # -> 2        a counted flag
parser.parse_args(["--no-tree"]).add_tree               # -> False
parser.parse_args(["--overwrite", "clobber"])           # exits with code 2 — not one of the four policies
```

**The choices come from the registry.** `--format` lists the registered renderers and `--overwrite` the values
of `OverwritePolicy`, so a new format or policy appears in the help without a change in the parser. That is why
**add-ons must be loaded before the parser is built**.

**`--dry-run` defaults to `None`.** *"Not given"* is different from *"no"*: the wizard asks about a dry run
only when the flag was not given.

**`-o` is a folder.** The file name comes from the profile, so several profiles in one run write several
files side by side.

<details>
<summary>🔍 Under the hood</summary>

```python
def build_parser() -> argparse.ArgumentParser:

    # 1. Description and the three optional positionals
    parser = argparse.ArgumentParser(
        prog="simplibs-extractor",
        description="Extract the files of a folder into one document.",
        epilog="Also: simplibs-extractor init [FOLDER]  (writes a local extract_here.py script).",
    )
    parser.add_argument("system", nargs="?", help="a system (python), or full profile keys (python/code-clean)")
    parser.add_argument("profiles", nargs="?", help="profile names, comma separated (code-clean,data-all)")
    parser.add_argument("source", nargs="?", type=Path, help="the folder to extract from")

    # 2. Where and how the output is written
    parser.add_argument("-o", "--output", type=Path, metavar="FOLDER", help="output FOLDER (default: the source)")
    parser.add_argument("--format", choices=list_formats(), help="output format (default: the profile's)")
    parser.add_argument("--overwrite", choices=get_args(OverwritePolicy), default="overwrite",
                        help="what to do when the output exists (default: overwrite)")
    parser.add_argument("--no-tree", dest="add_tree", action="store_false", default=True,
                        help="leave the directory tree out of the output")
    parser.add_argument("--dry-run", action="store_true", default=None,
                        help="plan and report, write nothing")

    # 3. How much to say
    parser.add_argument("-q", "--quiet", action="store_true", help="only errors")
    parser.add_argument("-v", "--verbose", action="count", default=0, help="more detail (-vv for everything)")
    parser.add_argument("--no-color", action="store_true", help="plain text, no colors")

    # 4. Questions about the registry, answered without extracting
    parser.add_argument("--list-systems", action="store_true", help="list the registered systems and exit")
    parser.add_argument("--list-profiles", metavar="SYSTEM", help="list the profiles of a system and exit")

    return parser
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `normalize_positionals`

**Sorts out which positional word is a system, profiles or the source.** `argparse` cannot tell three optional
positionals apart; this is the one place that guesses, and it guesses from the registry first and from the
disk second.

**Parameters:**

| Name   | Type                 | Description              |
|--------|----------------------|--------------------------|
| `args` | `argparse.Namespace` | The parsed arguments.    |

**Returns:** a **copy** of the namespace with `system`, `profiles` and `source` assigned correctly; `args` is
not changed, so the caller can still see what was typed.

**Raises:**
`ParamError` (`EXTRACTOR_CONFIG_INVALID`) — full profile keys are followed by two more words.

**Example usage:**

```python
from simplibs.extractor.cli import build_parser, normalize_positionals

def sort_out(*words):
    return normalize_positionals(build_parser().parse_args(list(words)))

args = sort_out("python", "code-clean", "my_project")
args.system, args.profiles, args.source                 # -> ('python', 'code-clean', Path('my_project'))      nothing to sort

args = sort_out("generic/all", "my_project")
args.system, args.profiles, args.source                 # -> (None, 'generic/all', Path('my_project'))         full keys, then the source

args = sort_out("my_project")                           # a folder that is not a registered system or key
args.system, args.profiles, args.source                 # -> (None, None, Path('my_project'))                  the source; profiles will be asked

sort_out("generic/all", "a", "b")                       # raises ParamError — full keys followed by two more words
```

**The order of the guesses.**

| #   | The first word is …                                                      | It becomes                                   |
|----:|--------------------------------------------------------------------------|----------------------------------------------|
| 1   | alone, **not** a registered system or key, and an existing folder        | the **source**                               |
| 2   | contains `/` or `,` (full keys); the second word, if any, is the source  | the **profiles** (`system` is cleared)       |
| 3   | anything else                                                            | left as typed: system, profiles, source      |

A registered system or key is **always** a profile reference, even if a folder of the same name exists:
`python` means the system. Only a word that is not a profile reference and is a folder becomes the source.

<details>
<summary>🔍 Under the hood</summary>

```python
def normalize_positionals(args: argparse.Namespace) -> argparse.Namespace:
    system, profiles, source = args.system, args.profiles, args.source

    # 1. A single word that is a folder and no known system or key is the source
    if system and profiles is None and source is None and not is_profile_reference(system) and Path(system).is_dir():
        system, source = None, Path(system)

    # 2. A first word with full keys (`generic/all` or `a,b`) is the list of profiles; the next one is the source
    elif system and ("/" in system or "," in system):
        if source is not None:
            raise_too_many_positionals_error(system, profiles, source)
        if profiles is not None:
            source = Path(profiles)
        profiles, system = system, None

    # 3. Return a copy, so the caller can still see what was typed
    return argparse.Namespace(**{**vars(args), "system": system, "profiles": profiles, "source": source})
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `collect_profile_keys`

**Gets the profile keys from the command line, or asks for them** — command line first, question second.

**Parameters:**

| Name   | Type                 | Description                        |
|--------|----------------------|------------------------------------|
| `args` | `argparse.Namespace` | The normalized arguments.          |

**Returns:** the full keys as a `list[str]`, in the order given.

**Raises:**
`StateError` (`CLI_NOT_INTERACTIVE`, from `simplibs-cli`) — profiles are missing and there is nobody to ask.
`ParamError` (`EXTRACTOR_CONFIG_INVALID`) — the chosen system has no registered profile.
`ParamError` (`EXTRACTOR_PROFILE_INVALID`) — from `expand_profile_keys`, e.g. a name without a system.

**Example usage:**

```python
from simplibs.extractor.cli import build_parser, collect_profile_keys, normalize_positionals

def sort_out(*words):
    return normalize_positionals(build_parser().parse_args(list(words)))

collect_profile_keys(sort_out("python", "code-clean,data-all", "my_project"))
# -> ['python/code-clean', 'python/data-all']      given: no question

collect_profile_keys(sort_out("generic/all", "my_project"))
# -> ['generic/all']

collect_profile_keys(sort_out("my_project"))
# in a terminal: asks for the system, then for the profiles of that system
# without a terminal: raises StateError — a card that says no profile was given
```

**Why a card and not a hang.** `simplibs-extractor python code-clean .` runs without asking anything. Leave the
profiles out and a terminal is asked; a pipe or a CI job gets a card saying what to pass.

**An unknown system is checked before the question.** The multi-choice prompt has nothing to offer for a system
without profiles, so the refusal comes first.

<details>
<summary>🔍 Under the hood</summary>

```python
def collect_profile_keys(args: argparse.Namespace) -> list[str]:

    # 1. Given on the command line: just expand them
    if args.profiles:
        return expand_profile_keys(args.system, args.profiles)

    # 2. Missing: a terminal can be asked, a pipe or a CI job gets a card instead of a hang
    require_interactive("no profile was given - pass SYSTEM PROFILES, or run in a terminal")

    # 3. The system: given, or asked
    system = args.system or prompt_choice("System", system_options())
    options = profile_options(system)
    if not options:
        raise_unknown_system_error(system)

    # 4. The profiles of that system
    names = prompt_multi_choice("Profiles", options)
    return expand_profile_keys(system, list(names))
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `collect_source`

**Gets the source folder from the command line, or asks for it.** The same rule as for the profiles: command
line first, question second, card instead of a hang.

**Parameters:**

| Name   | Type                 | Description                        |
|--------|----------------------|------------------------------------|
| `args` | `argparse.Namespace` | The normalized arguments.          |

**Returns:** the normalized `Path` of an existing folder.

**Raises:**
`StateError` (`CLI_NOT_INTERACTIVE`) — the source is missing or is not a folder, and there is nobody to ask.

**Example usage:**

```python
from simplibs.extractor.cli import build_parser, collect_source, normalize_positionals

def sort_out(*words):
    return normalize_positionals(build_parser().parse_args(list(words)))

collect_source(sort_out("generic/all", "my_project"))    # -> Path('/home/me/my_project')     a good value is used as it is
collect_source(sort_out("generic/all"))                  # in a terminal: asks; elsewhere: raises StateError
collect_source(sort_out("generic/all", "not_a_folder"))  # in a terminal: says so and asks again; elsewhere: raises StateError
```

**Why the check comes first.** `resolve_or_prompt` would ask in any case; the card has to come first so a CI
job learns **which argument** is missing.

<details>
<summary>🔍 Under the hood</summary>

```python
def collect_source(args: argparse.Namespace) -> Path:

    # 1. Anything that is not a usable folder needs an answer; without a terminal that is a card
    if args.source is None or not Path(args.source).is_dir():
        require_interactive("the SOURCE folder is missing or is not a folder")

    # 2. A good value is used as it is; a bad or missing one is replaced by a question
    answer = resolve_or_prompt(
        args.source,
        is_valid=lambda value: value is not None and Path(value).is_dir(),
        prompt=lambda: prompt_path("Source folder", kind="dir", must_exist=True),
        invalid_message=f"'{args.source}' is not a folder.",
    )
    return normalize_path(answer)
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `collect_dry_run`

**Decides whether this run is a dry run** — asked only of a person who is already being asked.

**Parameters:**

| Name    | Type                 | Description                                                                 |
|---------|----------------------|-----------------------------------------------------------------------------|
| `args`  | `argparse.Namespace` | The normalized arguments.                                                   |
| `asked` | `bool`               | Whether the person was already asked something (a profile or the source).   |

**Returns:** a `bool`.

| `--dry-run` given | `asked` | Terminal | Result                                           |
|:-----------------:|:-------:|:--------:|--------------------------------------------------|
| yes               | any     | any      | `True` — the flag decides                        |
| no                | yes     | yes      | **asked**: *"Dry run (write nothing)?"*, default *no* |
| no                | no      | any      | `False` — someone who typed everything wants it to run |
| no                | yes     | no       | `False` — nobody to ask                          |

**Example usage:**

```python
from simplibs.extractor.cli import build_parser, collect_dry_run, normalize_positionals

args = normalize_positionals(build_parser().parse_args(["generic/all", "my_project", "--dry-run"]))
collect_dry_run(args, asked=False)                      # -> True       the flag decides

args = normalize_positionals(build_parser().parse_args(["generic/all", "my_project"]))
collect_dry_run(args, asked=False)                      # -> False      a complete command: no extra question
```

**Why only inside the wizard.** The first draft asked every time in a terminal, including after a complete
command line — one question too many for someone who typed everything. The caller knows whether the wizard
asked anything; this function only applies the rule.

<details>
<summary>🔍 Under the hood</summary>

```python
def collect_dry_run(args: argparse.Namespace, asked: bool) -> bool:

    # 1. The flag decides
    if args.dry_run is not None:
        return args.dry_run

    # 2. A person who typed the full command wants it to run, not another question
    if asked and is_interactive():
        return prompt_confirm("Dry run (write nothing)?", default=False)

    return False
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `build_configs`

**Makes one `ExtractionConfig` per profile key** — the last step of the command line; `extract_many` runs the
result.

**Parameters:**

| Name      | Type                 | Description                              |
|-----------|----------------------|------------------------------------------|
| `args`    | `argparse.Namespace` | The normalized arguments.                |
| `keys`    | `Sequence[str]`      | The full profile keys.                   |
| `source`  | `Path`               | The source folder.                       |
| `dry_run` | `bool`               | Whether the run only plans.              |

**Returns:** the configs, in the order of the keys. Each one writes `<output folder>/<profile.output_name>`;
the output folder is `-o`, or the source itself.

**Raises:**
`NotFoundError` (`EXTRACTOR_PROFILE_NOT_FOUND`) — a key is not registered.
`ParamError` (`EXTRACTOR_CONFIG_INVALID`) — the output folder is a file, or two profiles would write the same
file.

**Example usage:**

```python
from pathlib import Path
from simplibs.extractor.cli import build_configs, build_parser, normalize_positionals

args = normalize_positionals(build_parser().parse_args(["generic/all", "my_project", "--overwrite", "unique"]))

configs = build_configs(args, ["generic/all"], Path("my_project"), dry_run=False)
configs[0].profile                                      # -> 'generic/all'
configs[0].target.name                                  # -> 'extraction.md'          the file name comes from the profile
configs[0].target.parent.name                           # -> 'my_project'             the output folder is the source
configs[0].overwrite                                    # -> 'unique'
configs[0].format                                       # -> None                     each profile uses its own format

build_configs(args, ["python/nope"], Path("my_project"), dry_run=False)         # raises NotFoundError — before anything runs
build_configs(args, ["generic/all", "generic/all"], Path("my_project"), False)  # raises ParamError — one file, written twice
```

With `-o out` the same run writes `out/extraction.md`; if `out` is an existing **file**, the command is refused:
`-o` takes a folder.

**Checked before anything runs.** A mistyped key, a file given as the output folder and two profiles aiming at
one file are all the person's mistakes, and cost nothing to find here. `extract_many` would report them too — but
only after the earlier profiles had already written their files.

<details>
<summary>🔍 Under the hood</summary>

```python
def build_configs(
    args: argparse.Namespace,
    keys: Sequence[str],
    source: Path,
    dry_run: bool,
) -> list[ExtractionConfig]:

    # 1. The output folder: `-o` or the source itself; it must not be a file
    out_dir = normalize_path(args.output) if args.output else normalize_path(source)
    if out_dir.is_file():
        raise_output_is_file_error(out_dir)

    # 2. One config per key; an unknown key fails here, before anything runs
    configs = [
        ExtractionConfig(
            source=source,
            target=out_dir / get_profile(key).output_name,
            profile=key,
            format=args.format,
            overwrite=args.overwrite,
            dry_run=dry_run,
            add_tree=args.add_tree,
        )
        for key in keys
    ]

    # 3. Two profiles with the same output name would overwrite each other
    targets = [config.target for config in configs]
    if len(set(targets)) != len(targets):
        raise_duplicate_output_error(keys)

    return configs
```

</details>

[▲ Back to top](#-table-of-contents)

---

### `handle_list_options`

**Answers `--list-systems` and `--list-profiles`** from the registry. Nothing is extracted.

**Parameters:**

| Name   | Type                 | Description                        |
|--------|----------------------|------------------------------------|
| `args` | `argparse.Namespace` | The normalized arguments.          |

**Returns:** `True` if a list was printed (the command is finished), `False` if no list was asked for.

**Raises:**
`ParamError` (`EXTRACTOR_CONFIG_INVALID`) — `--list-profiles` names a system without profiles.

**Example usage:**

```python
from simplibs.extractor.cli import build_parser, handle_list_options

handle_list_options(build_parser().parse_args(["--list-systems"]))              # -> True
handle_list_options(build_parser().parse_args(["--list-profiles", "generic"]))  # -> True
handle_list_options(build_parser().parse_args(["generic/all", "my_project"]))   # -> False     nothing to list

handle_list_options(build_parser().parse_args(["--list-profiles", "nope"]))     # raises ParamError — an unknown system
```

```text
$ simplibs-extractor --list-profiles generic
Profiles of generic:
  all - Every text file, unchanged.
```

**An unknown system is an error.** An empty list would look like *"no profiles exist"* and hide the typo.

<details>
<summary>🔍 Under the hood</summary>

```python
def handle_list_options(args: argparse.Namespace) -> bool:

    # 1. The systems
    if args.list_systems:
        print_choices(system_options(), title="Systems:")
        return True

    # 2. The profiles of one system; an unknown system is an error, not an empty list
    if args.list_profiles:
        options = profile_options(args.list_profiles)
        if not options:
            raise_list_unknown_system_error(args.list_profiles)
        print_choices(options, title=f"Profiles of {args.list_profiles}:")
        return True

    # 3. Nothing to list
    return False
```

</details>

[▲ Back to top](#-table-of-contents)

---

## Private helpers

Five small functions in `cli/_helpers`. They are not part of the interface; they are here so that nothing in the
command is a mystery.

### `describe_result`

**One line saying why an extraction failed** — for the batch report at the end of the command.
`ExtractionResult.success` is `False` for three different reasons, and the report says which:

| The result …                      | The line                                      |
|-----------------------------------|-----------------------------------------------|
| has `fatal` set                   | `<profile key>: <the fatal reason>`           |
| has failed files                  | `<profile key>: N file(s) failed`             |
| otherwise                         | `<profile key>: no file was selected`         |

<details>
<summary>🔍 Under the hood</summary>

```python
def describe_result(result: ExtractionResult) -> str:

    # 1. The whole run stopped
    if result.fatal:
        return f"{result.profile_key}: {result.fatal}"

    # 2. Some files failed
    if result.error_files:
        return f"{result.profile_key}: {len(result.error_files)} file(s) failed"

    # 3. Nothing failed, so nothing was selected
    return f"{result.profile_key}: no file was selected"
```

</details>

### `is_profile_reference`

**Whether a command-line word names a registered system or registered profile keys.** `simplibs-extractor src`
could mean *"the system `src`"* or *"the folder `src`"*; a registered system or key is a profile reference,
anything else may be a folder.

```python
is_profile_reference("generic")                         # -> True      a registered system
is_profile_reference("generic/all")                     # -> True      a registered key
is_profile_reference("generic/all, generic/all")        # -> True      a list made only of registered keys
is_profile_reference("./src")                           # -> False     may be a folder
is_profile_reference("generic/nope")                    # -> False     the shape of a key, but not registered
```

**Why the registry decides, not the shape of the word.** `generic/all` and `./src` both contain a slash.

<details>
<summary>🔍 Under the hood</summary>

```python
def is_profile_reference(value: str) -> bool:

    # 1. A system
    if value in list_systems():
        return True

    # 2. Full keys, one or several; every part must be registered
    keys = {profile.key for profile in list_profiles()}
    return all(part.strip() in keys for part in value.split(","))
```

</details>

### `print_error`

**Prints an error card to standard error** — the one way a refused command is shown. The card is printed as it
is: it already says what, why and how to fix it.

**Why not the logger.** A logger would prefix the first line of a multi-line card with the time and level and
break its frame. Standard error keeps diagnostics apart from a piped result.

<details>
<summary>🔍 Under the hood</summary>

```python
def print_error(error: BaseException) -> None:

    # 1. Diagnostics go to standard error, so they never mix with a piped result
    print(error, file=sys.stderr)
```

</details>

### `profile_options`

**`{name: description}` of one system's profiles**, sorted by name; **empty for an unknown system** — which is
how the caller learns that a system does not exist. It feeds `--list-profiles` and the question *"Which
profiles?"*.

```python
profile_options("generic")                              # -> {'all': 'Every text file, unchanged.'}
profile_options("nope")                                 # -> {}
```

<details>
<summary>🔍 Under the hood</summary>

```python
def profile_options(system: str) -> dict[str, str]:

    # 1. The names are the system's own (`code-clean`), without the `system/` part
    return {profile.name: profile.description for profile in list_profiles(system)}
```

</details>

### `system_options`

**`{system: "N profile(s)"}` of every registered system**, sorted. One function for both `--list-systems` and
the first question, so a list and a question never disagree about which systems exist.

```python
system_options()                                        # -> {'generic': '1 profile(s)'}      without add-ons
```

<details>
<summary>🔍 Under the hood</summary>

```python
def system_options() -> dict[str, str]:

    # 1. One entry per system, with the number of its profiles
    return {system: f"{len(list_profiles(system))} profile(s)" for system in list_systems()}
```

</details>

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../README.md#-the-command-line)
