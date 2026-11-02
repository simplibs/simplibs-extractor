# 🧪 `testing` — Testing the Profiles of an Add-on

The `testing` package holds **one tool and its three blades** for testing a `Profile`: `assert_profile` takes the profile
and a table of expectations and checks everything a profile promises — what it is called and what it writes, which files
it takes, and what its steps do to a text. It is made for the **add-ons** of the extractor
(for example `simplibs-extractor-python` and `simplibs-extractor-javascript`), which are made of profiles, and it replaces the test
module a hand-written profile test would need.

```python
from simplibs.extractor.testing import assert_profile
```

The package is **not** imported by `simplibs.extractor` itself — a program that only calls `extract()` has no use for
it — and it needs `pytest` 9 or newer, because the report is built from the native `subtests` fixture
(`pip install simplibs-extractor[dev]`).

## A profile test in one call

```python
# tests/test_profiles.py of an add-on
from simplibs.extractor.testing import assert_profile
from simplibs.extractor_python.profiles import PYTHON_SRC_CLEAN


def test_src_clean(subtests):
    assert_profile(
        subtests, PYTHON_SRC_CLEAN,
        expected_key="python/src-clean",
        expected_output_name="python_src_clean.md",
        included=("pkg/a.py", "pkg/__init__.py"),
        excluded=("tests/test_a.py", ".venv/x.py", "setup.py", "pkg/a.txt"),
        step_cases={".py": [("# c\nx = 1\n", "x = 1\n")]},
        unchanged_suffixes=(".txt",),
    )
```

That one call opens **eleven subtests**, each with a name that says what it checks:

```
[python/src-clean] test_key
[python/src-clean] test_description_is_one_line
[python/src-clean] test_output_name
[python/src-clean] test_selected_#index_0_pkg/a.py
[python/src-clean] test_selected_#index_1_pkg/__init__.py
[python/src-clean] test_left_out_#index_0_tests/test_a.py
[python/src-clean] test_left_out_#index_1_.venv/x.py
[python/src-clean] test_left_out_#index_2_setup.py
[python/src-clean] test_left_out_#index_3_pkg/a.txt
[python/src-clean] test_steps_.py_#index_0
[python/src-clean] test_no_step_#index_0_.txt
```

A failing value fails **its own subtest** and the others go on, so one run shows everything that is wrong with a
profile — not only the first thing.

## Three blades behind one call

`assert_profile` is a thin orchestrator. The work is done by three blades that you can also call alone:

| Blade                       | Checks                                                                      | Runs                                                   |
|-----------------------------|-----------------------------------------------------------------------------|--------------------------------------------------------|
| `assert_profile_identity`   | the key, a one-line description; the output name, format and exact description when given | **always**                              |
| `assert_profile_selection`  | which relative paths the `include` and `exclude` rules take                 | when `included` or `excluded` is given                 |
| `assert_profile_steps`      | what the steps do to a text, suffix by suffix                               | when `step_cases`, `unchanged_suffixes` or `cover_all_suffixes` is given |

A blade runs only when there is data for it: a profile with no rules and no steps (`generic/all`) has nothing to ask
there. How much to pin down is the decision of the test — `cover_all_suffixes=True` is the way to make it strict.

```python
from simplibs.extractor.testing import assert_profile
from simplibs.extractor_python.profiles import PYTHON_DATA_ALL

assert_profile(subtests, PYTHON_DATA_ALL, expected_key="python/data-all")      # two subtests: test_key, test_description_is_one_line
```

## What a failure says

The messages name the value, what was expected and what the profile did. Which rule is to blame is part of the message,
so the right one is looked at first:

```
[python/src-clean] test_key
    Expected the key 'python/src-clean-x', got 'python/src-clean'.
[python/src-clean] test_output_name
    Expected the output name 'other.md', got 'python_src_clean.md'.
[python/src-clean] test_selected_#index_0_tests/test_a.py
    Expected 'tests/test_a.py' to be taken, but the exclude rule matches it.
[python/src-clean] test_selected_#index_1_README.md
    Expected 'README.md' to be taken, but the include rule does not accept it.
[python/src-clean] test_left_out_#index_0_pkg/a.py
    Expected 'pkg/a.py' to be left out, but the profile takes it.
[python/src-clean] test_steps_.py_#index_0
    Expected the steps for '.py' to turn '# c\nx = 1\n' into 'x = 1', got 'x = 1\n'.
[x/y] test_every_suffix_has_a_case
    The steps have suffixes without a case: ['.b'].
```

A **mistake of the test itself** is not a failed subtest but an `AssertionError` raised at once, before any subtest, with
the reason: a path in both `included` and `excluded`, a suffix that has a case and is also in `unchanged_suffixes`, a
"suffix" such as `"*"` or `".PY"` that no file can have, or a first argument that is not a `Profile`.

## What it does not do

| Not here                                                                        | Where it belongs                                              |
|---------------------------------------------------------------------------------|---------------------------------------------------------------|
| That the profile is **registered** (`get_profile(key) is profile` after `register_all`) | the test of the add-on's plugin, once for all its profiles |
| That the output **format is registered**                                        | the run itself checks it; a custom format is registered by the add-on, not by the profile |
| That a step **warns** on a file it cannot handle (the file is then `partial`) | a focused test with `pytest.warns(UserWarning)` beside this call |
| A **run over real files**, with the rules of a config added                     | an integration test beside this call                          |
| A long realistic file and its exact result                                      | a focused test beside this call                               |

Whether a key part is usable, whether the output name is portable and whether a format has the right shape is checked when
a `Profile` is **built**, so it needs no test here.

---

## 🧭 Table of Contents

* [`assert_profile`](#assert_profile)
* [`assert_profile_identity`](#assert_profile_identity)
* [`assert_profile_selection`](#assert_profile_selection)
* [`assert_profile_steps`](#assert_profile_steps)
* [Errors of this package](#errors-of-this-package)

[⬅️ Back to main README](../README.md#-testing--testing-a-profile)

---

### `assert_profile`

**The master orchestrator: tests a profile through all three blades with one call.**

Imported from `simplibs.extractor.testing`. Everything after the first two arguments is keyword-only.

**Parameters:**

| Name                   | Type                                          | Default      | Description                                                                                                  |
|------------------------|-----------------------------------------------|--------------|--------------------------------------------------------------------------------------------------------------|
| `subtests`             | `Any`                                         | *(required)* | The native pytest `subtests` fixture.                                                                        |
| `profile`              | `Profile`                                     | *(required)* | The profile under test.                                                                                      |
| `expected_key`         | `str`                                         | *(required)* | The registry key (`"python/code-clean"`). *(keyword-only)*                                                   |
| `expected_output_name` | `str \| None`                                 | `None`       | If given, `profile.output_name` must equal it. *(keyword-only)*                                              |
| `expected_format`      | `str \| None`                                 | `None`       | If given, `profile.format` must equal it. *(keyword-only)*                                                   |
| `expected_description` | `str \| None`                                 | `None`       | If given, `profile.description` must equal it exactly; without it only the generic contract is checked. *(keyword-only)* |
| `included`             | `Sequence[str]`                               | `()`         | Paths relative to the source (`"pkg/a.py"`) that the profile must take. *(keyword-only)*                     |
| `excluded`             | `Sequence[str]`                               | `()`         | Relative paths that the profile must leave out. *(keyword-only)*                                             |
| `step_cases`           | `Mapping[str, Sequence[tuple[str, str]]] \| None` | `None`   | `{suffix: [(text, expected_text), ...]}` for the steps. *(keyword-only)*                                     |
| `unchanged_suffixes`   | `Sequence[str]`                               | `()`         | Suffixes for which no step may apply. *(keyword-only)*                                                       |
| `cover_all_suffixes`   | `bool`                                        | `False`      | Every suffix key of the steps must have a case. *(keyword-only)*                                             |
| `verbose`              | `bool`                                        | `True`       | One isolated subtest per check. *(keyword-only)*                                                             |
| `intro`                | `str`                                         | `""`         | Prefix of the subtest names; derived from the key when left empty. *(keyword-only)*                          |

**Returns:** `None`.

**Raises:** `AssertionError` — `profile` is not a `Profile`; or a mistake of the test (see
[What a failure says](#what-a-failure-says)); or, with `verbose=False`, the first check that fails. With `verbose=True`
a failing check is a failed subtest and does not raise here.

**Example usage:**

```python
from simplibs.extractor.testing import assert_profile
from simplibs.extractor_python.profiles import PYTHON_CODE_CLEAN

def test_code_clean(subtests):
    assert_profile(
        subtests, PYTHON_CODE_CLEAN,
        expected_key="python/code-clean",
        expected_output_name="python_code_clean.md",
        included=("pkg/a.py", "tests/test_a.py"),                    # code-clean takes the tests too
        excluded=("pkg/a.txt", "pkg/.hidden.py", "pkg/__pycache__/a.py"),
        step_cases={".py": [("import os  # c\nx = 1\n", "import os\nx = 1\n")]},
        unchanged_suffixes=(".md",),
        cover_all_suffixes=True,                                     # every suffix of the steps has a case
    )
```

**The prefix of the names.** With `intro` left empty the subtests are named `[python/code-clean] test_key`, so the key
is the group name and nobody has to invent one. With `intro="python"` the names read `python test_key` — useful when one
test runs several profiles through a shared prefix.

**One call per profile.** A test module of an add-on is a list of these calls, one per profile; the data of each is the
documentation of what the profile promises.

**`verbose=False`.** No subtests are opened and the first failing check raises a plain `AssertionError` — for a debugger,
or for a place where the `subtests` fixture is not wanted.

<details>
<summary>🔍 Under the hood</summary>

```python
def assert_profile(
    subtests: Any,
    profile: Profile,
    *,
    expected_key: str,
    expected_output_name: str | None = None,
    expected_format: str | None = None,
    expected_description: str | None = None,
    included: Sequence[str] = (),
    excluded: Sequence[str] = (),
    step_cases: Mapping[str, Sequence[tuple[str, str]]] | None = None,
    unchanged_suffixes: Sequence[str] = (),
    cover_all_suffixes: bool = False,
    verbose: bool = True,
    intro: str = "",
) -> None:
    assert isinstance(profile, Profile), (
        f"assert_profile expects a Profile instance, got {type(profile).__name__}."
    )

    prefix = f"{intro}[{profile.key}] " if intro == "" else f"{intro} "

    # 1. Name tags: key, description, output name, format
    assert_profile_identity(
        subtests,
        profile,
        expected_key=expected_key,
        expected_output_name=expected_output_name,
        expected_format=expected_format,
        expected_description=expected_description,
        verbose=verbose,
        intro=prefix,
    )

    # 2. Which files it takes
    if included or excluded:
        assert_profile_selection(
            subtests,
            profile,
            included,
            excluded,
            verbose=verbose,
            intro=prefix,
        )

    # 3. What its steps do
    if step_cases or unchanged_suffixes or cover_all_suffixes:
        assert_profile_steps(
            subtests,
            profile,
            step_cases or {},
            unchanged_suffixes,
            cover_all_suffixes=cover_all_suffixes,
            verbose=verbose,
            intro=prefix,
        )
```

The orchestrator does three things: it guards the type (`isinstance(profile, Profile)` before any blade, so a key string
or a class gives one clear message instead of an `AttributeError` somewhere inside), builds the prefix, and starts the
blades. **No outer subtest wraps them**: each blade opens a subtest per value, and an outer one would never see a failure
of an inner one — the prefix (`[python/src-clean] `) passed down as `intro` is what groups them in the report.

The two blades behind `if` run only when there is data for them; the identity blade runs always.

</details>

[▲ Back to top](#-table-of-contents)

---

### `assert_profile_identity`

**Verifies the name tags of a profile: what it is called and what it writes.**

Imported from `simplibs.extractor.testing.asserts`. It checks what a person sees of a profile before it runs: its key, the
line in `--list-profiles`, the name of the file it writes and the format.

**Parameters:**

| Name                   | Type          | Default      | Description                                                                                      |
|------------------------|---------------|--------------|--------------------------------------------------------------------------------------------------|
| `subtests`             | `Any`         | *(required)* | The native pytest `subtests` fixture.                                                            |
| `profile`              | `Profile`     | *(required)* | The profile under test.                                                                          |
| `expected_key`         | `str`         | *(required)* | The registry key. *(keyword-only)*                                                               |
| `expected_output_name` | `str \| None` | `None`       | If given, `profile.output_name` must equal it. *(keyword-only)*                                  |
| `expected_format`      | `str \| None` | `None`       | If given, `profile.format` must equal it. *(keyword-only)*                                       |
| `expected_description` | `str \| None` | `None`       | If given, `profile.description` must equal it exactly. *(keyword-only)*                          |
| `verbose`              | `bool`        | `True`       | One isolated subtest per check. *(keyword-only)*                                                 |
| `intro`                | `str`         | `""`         | Prefix of the subtest names, used **as it is** (`assert_profile` adds the key and the space). *(keyword-only)* |

**Returns:** `None`.

**Raises:** `AssertionError` — `profile` is not a `Profile`; with `verbose=False`, a check that fails.

**Example usage:**

```python
from simplibs.extractor.testing.asserts import assert_profile_identity
from simplibs.extractor_python.profiles import PYTHON_SRC_CLEAN

def test_identity(subtests):
    assert_profile_identity(
        subtests, PYTHON_SRC_CLEAN,
        expected_key="python/src-clean",
        expected_output_name="python_src_clean.md",
        expected_description="Like code-clean, without tests, configuration, environments and build folders",
        intro="[python/src-clean] ",
    )
```

| Subtest                              | Runs                      | Fails when                                                            |
|--------------------------------------|---------------------------|-----------------------------------------------------------------------|
| `test_key`                           | always                    | `profile.key` differs from `expected_key`                              |
| `test_description_is_one_line`       | always                    | the description is blank or has more than one line                    |
| `test_description_expected_text`     | `expected_description`    | the description is not exactly the expected text                       |
| `test_output_name`                   | `expected_output_name`    | the output name differs                                                |
| `test_format`                        | `expected_format`         | the format differs                                                     |

**The description always has to be a line.** `Profile` allows an empty description (it is the default), but a profile that
is listed with an empty line is a profile nobody can choose — so a non-blank, one-line description is the generic
contract, and the exact text is opt-in, as with `describe()` of a rule.

**Pin what a person finds on the disk.** A profile that keeps the defaults can leave `expected_output_name` and
`expected_format` out; one that names its output (`python_src_clean.md`) should pin it, because a rename changes what
people find in their folders.

<details>
<summary>🔍 Under the hood</summary>

```python
def assert_profile_identity(
    subtests: Any,
    profile: Profile,
    *,
    expected_key: str,
    expected_output_name: str | None = None,
    expected_format: str | None = None,
    expected_description: str | None = None,
    verbose: bool = True,
    intro: str = "",
) -> None:
    assert isinstance(profile, Profile), (
        f"assert_profile_identity expects a Profile instance, got {type(profile).__name__}."
    )

    # 1. The key
    with maybe_subtest(
        subtests,
        name=f"{intro}test_key",
        verbose=verbose,
    ):
        assert profile.key == expected_key, (
            f"Expected the key {expected_key!r}, got {profile.key!r}."
        )

    # 2. The description: shown by the listing commands, so one non-blank line
    with maybe_subtest(
        subtests,
        name=f"{intro}test_description_is_one_line",
        verbose=verbose,
    ):
        description = profile.description
        assert isinstance(description, str) and description.strip() != "", (
            f"Expected a non-blank description (the listing commands show it), got {description!r}."
        )
        assert "\n" not in description.strip(), (
            f"Expected a one-line description, got {description!r}."
        )

    # 3. The optional exact values
    if expected_description is not None:
        with maybe_subtest(
            subtests,
            name=f"{intro}test_description_expected_text",
            verbose=verbose,
        ):
            assert profile.description == expected_description, (
                f"Expected the description {expected_description!r}, got {profile.description!r}."
            )

    if expected_output_name is not None:
        with maybe_subtest(
            subtests,
            name=f"{intro}test_output_name",
            verbose=verbose,
        ):
            assert profile.output_name == expected_output_name, (
                f"Expected the output name {expected_output_name!r}, got {profile.output_name!r}."
            )

    if expected_format is not None:
        with maybe_subtest(
            subtests,
            name=f"{intro}test_format",
            verbose=verbose,
        ):
            assert profile.format == expected_format, (
                f"Expected the format {expected_format!r}, got {profile.format!r}."
            )
```

Each check is its own subtest, guarded by `maybe_subtest` of `simplibs-exception`: with `verbose=True` it opens a pytest
subtest, with `verbose=False` it is a plain block. The optional values are compared **only when given** — a `None` means
"I do not pin this".

</details>

[▲ Back to top](#-table-of-contents)

---

### `assert_profile_selection`

**Verifies which relative paths the `include` and `exclude` rules of a profile take.**

Imported from `simplibs.extractor.testing.asserts`. A profile is, first of all, a decision about files; this blade asks it
the way the select phase does — with the path relative to the source folder. A file is **taken** when `include` accepts it
(or there is no `include`) and `exclude` does not match it (or there is no `exclude`).

**Parameters:**

| Name       | Type            | Default      | Description                                                                                          |
|------------|-----------------|--------------|------------------------------------------------------------------------------------------------------|
| `subtests` | `Any`           | *(required)* | The native pytest `subtests` fixture.                                                                |
| `profile`  | `Profile`       | *(required)* | The profile under test.                                                                              |
| `included` | `Sequence[str]` | *(required)* | Paths relative to the source (`"pkg/a.py"`, written with `/`) that the profile must take.            |
| `excluded` | `Sequence[str]` | *(required)* | Paths that the profile must leave out, whichever rule does it.                                       |
| `verbose`  | `bool`          | `True`       | One isolated subtest per path. *(keyword-only)*                                                      |
| `intro`    | `str`           | `""`         | Prefix of the subtest names, used as it is. *(keyword-only)*                                         |

**Returns:** `None`.

**Raises:** `AssertionError` — `profile` is not a `Profile`; a path is in **both** lists (the test could never pass);
with `verbose=False`, a path that is judged wrongly.

**Example usage:**

```python
from simplibs.extractor.testing.asserts import assert_profile_selection
from simplibs.extractor_python.profiles import PYTHON_SRC_CLEAN

def test_selection(subtests):
    assert_profile_selection(
        subtests, PYTHON_SRC_CLEAN,
        included=("pkg/a.py", "pkg/__init__.py", "pkg/latest_data.py"),
        excluded=("tests/test_a.py", "setup.py", ".venv/lib/x.py", "pkg/a.txt"),
    )
```

| Subtest                              | Meaning                                                                    |
|--------------------------------------|----------------------------------------------------------------------------|
| `test_selected_#index_{i}_{path}`    | the path must be taken                                                     |
| `test_left_out_#index_{i}_{path}`    | the path must be left out                                                  |

**Paths as text, judged as a `Path`.** You write `"tests/test_a.py"`; the blade makes a `Path` of it, the type the rules
receive in a real run, so a rule that looks at the parent folders or the name sees what it would see there.

**The reason is part of the message.** A failure says whether the `include` rule did not accept the path ("the include
rule does not accept it") or the `exclude` rule matched it ("the exclude rule matches it"), so the right rule is looked at
first.

**`exclude` beats `include`.** A path of `excluded` fails only if the profile takes it; it does not matter which rule
leaves it out. A test of a path that every rule accepts and `exclude` rejects (`tests/test_a.py` for `src-clean`) is the
most common one — and the one most easily forgotten.

<details>
<summary>🔍 Under the hood</summary>

```python
def assert_profile_selection(
    subtests: Any,
    profile: Profile,
    included: Sequence[str],
    excluded: Sequence[str],
    *,
    verbose: bool = True,
    intro: str = "",
) -> None:
    assert isinstance(profile, Profile), (
        f"assert_profile_selection expects a Profile instance, got {type(profile).__name__}."
    )
    overlap = sorted(set(included) & set(excluded))
    assert not overlap, (
        f"assert_profile_selection received paths that are both included and excluded: {overlap}."
    )

    def why_left_out(path: str) -> str | None:
        """The reason the profile does not take the path; None if it takes it."""
        relative = Path(path)
        if profile.include is not None and not profile.include(relative):
            return "the include rule does not accept it"
        if profile.exclude is not None and profile.exclude(relative):
            return "the exclude rule matches it"
        return None

    # 1. Paths the profile must take
    for index, path in enumerate(included):
        with maybe_subtest(
            subtests,
            name=f"{intro}test_selected_#index_{index}_{path}",
            verbose=verbose,
        ):
            reason = why_left_out(path)
            assert reason is None, f"Expected {path!r} to be taken, but {reason}."

    # 2. Paths the profile must leave out
    for index, path in enumerate(excluded):
        with maybe_subtest(
            subtests,
            name=f"{intro}test_left_out_#index_{index}_{path}",
            verbose=verbose,
        ):
            assert why_left_out(path) is not None, (
                f"Expected {path!r} to be left out, but the profile takes it."
            )
```

The two conditions are written here again (three lines, in `why_left_out`) because the select phase has no function that
answers for one path without a folder on the disk. `why_left_out` returns the **reason** the profile does not take a path,
or `None` when it takes it; the two loops only ask it. A run over real files, with the rules of a config on top, belongs
to the integration tests of the add-on.

</details>

[▲ Back to top](#-table-of-contents)

---

### `assert_profile_steps`

**Verifies what the steps of a profile do to a text, suffix by suffix.**

Imported from `simplibs.extractor.testing.asserts`. The data is a table of `(text, expected_text)` pairs per suffix, so the
test reads as a list of examples. The steps are run by the **same functions** as in a real extraction (`apply_steps`,
`steps_for`), so the choice of the action — own suffix, fallback `"*"`, one action for all — is the one a run would make.

**Parameters:**

| Name                 | Type                                          | Default      | Description                                                                                          |
|----------------------|-----------------------------------------------|--------------|------------------------------------------------------------------------------------------------------|
| `subtests`           | `Any`                                         | *(required)* | The native pytest `subtests` fixture.                                                                |
| `profile`            | `Profile`                                     | *(required)* | The profile under test.                                                                              |
| `cases`              | `Mapping[str, Sequence[tuple[str, str]]]`     | *(required)* | `{suffix: [(text, expected_text), ...]}`; the suffix is a file suffix (`".py"`), never `"*"`.        |
| `unchanged_suffixes` | `Sequence[str]`                               | `()`         | Suffixes for which no step may apply at all.                                                         |
| `cover_all_suffixes` | `bool`                                        | `False`      | Every suffix key of a mapping of steps must have a case. *(keyword-only)*                            |
| `verbose`            | `bool`                                        | `True`       | One isolated subtest per check. *(keyword-only)*                                                     |
| `intro`              | `str`                                         | `""`         | Prefix of the subtest names, used as it is. *(keyword-only)*                                         |

**Returns:** `None`.

**Raises:** `AssertionError` — `profile` is not a `Profile`; a suffix is not a file suffix (lowercase, such as `".py"`);
a suffix has cases **and** is in `unchanged_suffixes`; with `verbose=False`, a check that fails.

**Example usage:**

```python
from simplibs.extractor.testing.asserts import assert_profile_steps
from simplibs.extractor_python.profiles import PYTHON_CODE_CLEAN

def test_steps(subtests):
    assert_profile_steps(
        subtests, PYTHON_CODE_CLEAN,
        {".py": [
            ("# c\nx = 1\n", "x = 1\n"),                          # a comment on its own line goes
            ("x = 1  # c\n", "x = 1\n"),                          # a trailing comment goes
        ]},
        unchanged_suffixes=(".txt", ".md"),                       # no step for these at all
        cover_all_suffixes=True,
    )
```

| Subtest                              | Meaning                                                                                  |
|--------------------------------------|------------------------------------------------------------------------------------------|
| `test_steps_{suffix}_#index_{i}`     | the steps turn the text of this pair into the expected text                              |
| `test_no_step_#index_{i}_{suffix}`   | no step applies to the suffix                                                            |
| `test_every_suffix_has_a_case`       | every suffix key of the steps (and the fallback `"*"`) has a case — only with `cover_all_suffixes` |

**`unchanged_suffixes` checks the choice, not the result.** It asks `steps_for(...)` and expects `None`: *no step applies*.
A pair whose expected text equals the input would also be green when a step existed and did nothing — so it is not a
substitute.

**`cover_all_suffixes` is opt-in.** A profile that maps every suffix of a language to the same action would need a case
for each; the person decides whether that is wanted. When it is, a suffix added to the profile later and never tested
fails here. The fallback `"*"` needs a case with a suffix that **no key names** (for example `".xyz"`), because that is how
it is reached. A profile whose `steps` is a single action (not a mapping) has no suffix keys, and the check does nothing.

**Only real suffixes.** Keys such as `"*"` or `".PY"` can never be the suffix of a file. Using one in a case is a mistake
of the test and fails at once with the reason.

<details>
<summary>🔍 Under the hood</summary>

```python
def assert_profile_steps(
    subtests: Any,
    profile: Profile,
    cases: Mapping[str, Sequence[tuple[str, str]]],
    unchanged_suffixes: Sequence[str] = (),
    *,
    cover_all_suffixes: bool = False,
    verbose: bool = True,
    intro: str = "",
) -> None:
    assert isinstance(profile, Profile), (
        f"assert_profile_steps expects a Profile instance, got {type(profile).__name__}."
    )
    for suffix in (*cases, *unchanged_suffixes):
        assert is_suffix_key(suffix) and suffix != "*", (
            f"assert_profile_steps expects file suffixes such as '.py' (lowercase), got {suffix!r}."
        )
    both = sorted(set(cases) & set(unchanged_suffixes))
    assert not both, (
        f"assert_profile_steps received suffixes that have cases and are also unchanged: {both}."
    )

    # 1. What the steps do to a text
    for suffix, pairs in cases.items():
        for index, (text, expected) in enumerate(pairs):
            with maybe_subtest(
                subtests,
                name=f"{intro}test_steps_{suffix}_#index_{index}",
                verbose=verbose,
            ):
                result = apply_steps(text, profile.steps, suffix)
                assert result == expected, (
                    f"Expected the steps for {suffix!r} to turn {text!r} into {expected!r}, got {result!r}."
                )

    # 2. Suffixes that no step touches
    for index, suffix in enumerate(unchanged_suffixes):
        with maybe_subtest(
            subtests,
            name=f"{intro}test_no_step_#index_{index}_{suffix}",
            verbose=verbose,
        ):
            step = steps_for(profile.steps, suffix)
            assert step is None, (
                f"Expected no step for {suffix!r}, but the profile applies {type(step).__name__}."
            )

    # 3. Nothing left untested (opt-in)
    if cover_all_suffixes and isinstance(profile.steps, Mapping):
        with maybe_subtest(
            subtests,
            name=f"{intro}test_every_suffix_has_a_case",
            verbose=verbose,
        ):
            keys = [key for key in profile.steps if key != "*"]
            missing = sorted(set(keys) - set(cases))
            assert not missing, f"The steps have suffixes without a case: {missing}."
            if "*" in profile.steps:
                assert set(cases) - set(keys), (
                    "The fallback '*' has no case: add a suffix that no key names (for example '.xyz')."
                )
```

The blade does not look into the mapping itself: `apply_steps` and `steps_for` are the functions the transform phase uses,
so a change in how a suffix is resolved (case, fallback, a new kind of mapping) is followed without a change here — and the
test cannot agree with a wrong profile. The two checks of the arguments come first and raise at once; then come the cases,
the unchanged suffixes and, on request, the coverage.

</details>

[▲ Back to top](#-table-of-contents)

---

## Errors of this package

The testing tools define **no exceptions and raise no cards**. What they raise is a plain `AssertionError`, as every test
helper does: from the check that failed (with `verbose=False`), or — always — from a **mistake of the test itself** (a
first argument that is not a `Profile`, a path in both lists, a suffix that is not a file suffix, a suffix that has cases
and is also unchanged). With `verbose=True` a failed check is reported by `pytest` as a failed subtest.

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../README.md#-testing--testing-a-profile)
