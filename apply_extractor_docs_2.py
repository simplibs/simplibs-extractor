"""Druhá dávka úprav dokumentace simplibs-extractor 0.2.0: složka `testing` a nová jména doplňků.

Spuštění: dej tento soubor do kořene knihovny (vedle složky `docs` a souboru `README.md`) a spusť ho.
Pouštěj ho až PO prvním skriptu (`apply_extractor_docs.py`).

Co dělá:
1. U každého souboru zkontroluje, že se každý hledaný text najde PŘESNĚ JEDNOU.
2. Jen když to platí pro celý soubor, provede všechny jeho úpravy a soubor uloží.
3. Když se něco nenajde, soubor nechá beze změny a vypíše, co přesně nesedí.

Skript jde pustit znovu: soubor, který už je upravený, pozná a přeskočí.
"""

from pathlib import Path


ROOT = Path(__file__).resolve().parent


def E(find: str, replace: str) -> tuple[str, str]:
    return find, replace


EDITS: dict[str, list[tuple[str, str]]] = {}

# ======================================================================
# CHANGELOG.md : složka `testing`
# ======================================================================
EDITS["CHANGELOG.md"] = [
    E('''* The run logs a partial file as a warning
''',
      '''* The run logs a partial file as a warning

#### Testing — tools for the add-ons

* `simplibs.extractor.testing` — a new package for testing the profiles of an add-on; the package root does not import it, and it needs `pytest` 9 or newer (the report is built from the native `subtests` fixture; `pip install simplibs-extractor[dev]`)
* `assert_profile(subtests, profile, ...)` — checks everything a profile promises in one call, with a subtest for each thing it checks, so one run shows everything that is wrong with a profile: the key and a one-line description, the output name and format, which relative paths the `include` and `exclude` rules take and leave out, and what the steps do to a text, suffix by suffix
* The three blades behind it, which can also be called alone from `simplibs.extractor.testing.asserts`: `assert_profile_identity`, `assert_profile_selection` and `assert_profile_steps`; a blade runs only when there is data for it
* A mistake of the test itself (a path in both lists, a suffix that no file can have, a first argument that is not a `Profile`) is an `AssertionError` raised at once, before any subtest; the tools define no exceptions of their own and raise no cards
* `testing` is the last layer of the package (`... ← scripts ← cli ← testing`): it may look at everything and nothing looks at it
'''),
    E('''* `README_EXTRACTOR_PLUGINS`: recommendations for the profiles of an add-on
''',
      '''* `README_EXTRACTOR_PLUGINS`: recommendations for the profiles of an add-on
* `README_EXTRACTOR_TESTING` (new): `assert_profile` and its three blades, and a `testing` section in the main `README`
'''),
]

# ======================================================================
# README.md : nová jména doplňků
# ======================================================================
EDITS["README.md"] = [
    E('''(`simplibs-code-extractor` is the first)''',
      '''(one add-on per language: `simplibs-extractor-python` and `simplibs-extractor-javascript` are the first)'''),
    E('''`pip install simplibs-code-extractor`''',
      '''`pip install simplibs-extractor-python`'''),
    E('''code = "simplibs.code_extractor:register_all"''',
      '''python = "simplibs.extractor_python:register_all"'''),
    E('''* **`simplibs-code-extractor`** — the first add-on: profiles for Python and React projects, built on this extractor.''',
      '''* **[`simplibs-extractor-python`](https://pypi.org/project/simplibs-extractor-python/)** and **[`simplibs-extractor-javascript`](https://pypi.org/project/simplibs-extractor-javascript/)** — the first add-ons, one per language: profiles for Python projects, and for JavaScript and TypeScript projects (React included), built on this extractor. More languages can follow the same way.'''),
]

# ======================================================================
# docs/README_EXTRACTOR_PLUGINS.md
# ======================================================================
EDITS["docs/README_EXTRACTOR_PLUGINS.md"] = [
    E('''What a Python project, a React project or your own kind of project needs''',
      '''What a Python project, a JavaScript project or your own kind of project needs'''),
    E('''pip install simplibs-code-extractor''',
      '''pip install simplibs-extractor-python'''),
    E('''code = "simplibs.code_extractor:register_all"''',
      '''python = "simplibs.extractor_python:register_all"'''),
    E('''# -> ['generic', 'python', 'react']      with simplibs-code-extractor installed''',
      '''# -> ['generic', 'python']               with simplibs-extractor-python installed'''),
    E('''# -> ['code']        with simplibs-code-extractor installed''',
      '''# -> ['python']      with simplibs-extractor-python installed'''),
    E('''The `plugins` package is the half that **finds** them.''',
      '''There is **one add-on per language**, so a person installs only what the project needs:
`simplibs-extractor-python` and `simplibs-extractor-javascript` are the first, and any other language can follow the same
way.

The `plugins` package is the half that **finds** them.'''),
    E('''| Depend on `simplibs-extractor>=0.2.0`''',
      '''| Test every profile with [`assert_profile`](README_EXTRACTOR_TESTING.md) from `simplibs.extractor.testing`. | One call checks the key, the output name, which files the profile takes and what its steps do. |
| Depend on `simplibs-extractor>=0.2.0`'''),
]

# ======================================================================
# docs/README_EXTRACTOR_REGISTRY.md
# ======================================================================
EDITS["docs/README_EXTRACTOR_REGISTRY.md"] = [
    E('''# -> ['generic', 'python', 'react']      with simplibs-code-extractor installed''',
      '''# -> ['generic', 'python']               with simplibs-extractor-python installed'''),
]

# ======================================================================
# docs/README_EXTRACTOR_CONSTANTS.md
# ======================================================================
EDITS["docs/README_EXTRACTOR_CONSTANTS.md"] = [
    E('''code = "simplibs.code_extractor:register_all"''',
      '''python = "simplibs.extractor_python:register_all"'''),
]

# ======================================================================
# docs/README_EXTRACTOR_TESTING.md
# ======================================================================
EDITS["docs/README_EXTRACTOR_TESTING.md"] = [
    E('''(`simplibs-extractor-python`, `simplibs-extractor-javascript`), which are made of profiles''',
      '''(for example `simplibs-extractor-python` and `simplibs-extractor-javascript`), which are made of profiles'''),
    E('''| A **run over real files**''',
      '''| That a step **warns** on a file it cannot handle (the file is then `partial`) | a focused test with `pytest.warns(UserWarning)` beside this call |
| A **run over real files**'''),
]


# ----------------------------------------------------------------------
# Provedení
# ----------------------------------------------------------------------
def apply_to_file(relative: str, edits: list[tuple[str, str]]) -> str:
    """Vrátí `done`, `skipped` (už upraveno) nebo `failed`; při selhání soubor nezmění."""

    path = ROOT / relative
    if not path.exists():
        print(f"  ! {relative}: soubor neexistuje")
        return "failed"

    text = path.read_bytes().decode("utf-8")
    crlf = "\r\n" in text
    work = text.replace("\r\n", "\n")

    # 1. Už upraveno? (všechny nové texty už v souboru jsou)
    if all(replace in work for _, replace in edits):
        print(f"  = {relative}: už je upraveno")
        return "skipped"

    # 2. Každý hledaný text musí být přesně jednou
    problems = []
    for find, _ in edits:
        count = work.count(find)
        if count != 1:
            problems.append(f"nalezeno {count}× místo 1×: {find.strip().splitlines()[0][:80]}")
    if problems:
        print(f"  ! {relative}: NIC NEZMĚNĚNO")
        for problem in problems:
            print(f"      - {problem}")
        return "failed"

    # 3. Provést
    for find, replace in edits:
        work = work.replace(find, replace, 1)
    path.write_bytes((work.replace("\n", "\r\n") if crlf else work).encode("utf-8"))
    print(f"  + {relative}: upraveno ({len(edits)} úprav)")
    return "done"


def main() -> None:
    results = [apply_to_file(relative, edits) for relative, edits in EDITS.items()]
    print(f"\nHotovo: {results.count('done')} upraveno, {results.count('skipped')} už bylo, {results.count('failed')} selhalo.")
    if "failed" in results:
        print("U souboru, který selhal, se nic nezměnilo. Pošli mi výpis nad touto větou.")


if __name__ == "__main__":
    main()
