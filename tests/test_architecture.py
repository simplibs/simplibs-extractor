import ast
from pathlib import Path
import pytest
import simplibs.extractor

PACKAGE = Path(simplibs.extractor.__file__).parent
TESTS = Path(__file__).parent

# Every layer looks only at the layers before it (to the left).
LAYERS = ["annotations", "constants", "definitions", "registry", "logic", "plugins", "scripts", "cli"]

ROOT_FILES = {"__init__.py", "__main__.py"}


def _sources() -> list[Path]:
    return sorted(path for path in PACKAGE.rglob("*.py") if "__pycache__" not in path.parts)


def _relative(path: Path) -> str:
    return path.relative_to(PACKAGE).as_posix()


def _parse(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _top_level_names(tree: ast.Module) -> set[str]:
    names: set[str] = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.Assign):
            names.update(target.id for target in node.targets if isinstance(target, ast.Name))
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.add(node.target.id)
    return names


def _imported_modules(path: Path, tree: ast.Module) -> list[list[str]]:
    """Every module this file imports from the package, as dotted parts such as ['simplibs', 'extractor', 'registry', ...]."""
    parts = ["simplibs", "extractor", *path.relative_to(PACKAGE).with_suffix("").parts]
    package = parts[:-1]      # the folder of a module, and the folder of an __init__ alike
    found: list[list[str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.level:
                base = package[: len(package) - (node.level - 1)]
                if node.module:
                    found.append(base + node.module.split("."))
                else:
                    found.extend(base + [alias.name] for alias in node.names)
            elif node.module and node.module.split(".")[:2] == ["simplibs", "extractor"]:
                found.append(node.module.split("."))
        elif isinstance(node, ast.Import):
            found.extend(alias.name.split(".") for alias in node.names if alias.name.split(".")[:2] == ["simplibs", "extractor"])
    return found


def test_the_package_was_found() -> None:
    assert len(_sources()) > 50


def test_every_layer_looks_only_at_the_layers_to_its_left() -> None:
    problems: list[str] = []
    for path in _sources():
        relative = _relative(path)
        if relative in ROOT_FILES:
            continue
        own = relative.split("/")[0]
        assert own in LAYERS, f"{relative}: its folder is not a known layer"
        for target in _imported_modules(path, _parse(path)):
            if len(target) < 3:
                problems.append(f"{relative}: imports the package root ({'.'.join(target)})")
                continue
            layer = target[2]
            if layer not in LAYERS:
                problems.append(f"{relative}: imports {'.'.join(target)}, which is not a known layer")
            elif LAYERS.index(layer) > LAYERS.index(own):
                problems.append(f"{relative}: layer '{own}' imports from the higher layer '{layer}' ({'.'.join(target)})")
    assert problems == []


def test_every_file_is_named_after_the_thing_it_defines() -> None:
    """One file, one thing: `register_profile.py` defines `register_profile`."""
    problems = [
        _relative(path)
        for path in _sources()
        if path.name not in ROOT_FILES and path.name != "__init__.py" and path.stem not in _top_level_names(_parse(path))
    ]
    assert problems == []


def test_every_file_ends_with_its_design_notes() -> None:
    problems = []
    for path in _sources():
        tree = _parse(path)
        if "_DESIGN_NOTES" not in _top_level_names(tree):
            problems.append(_relative(path))
        elif path.name != "__main__.py" and not (
            isinstance(tree.body[-1], ast.Assign)
            and getattr(tree.body[-1].targets[0], "id", None) == "_DESIGN_NOTES"
        ):
            problems.append(f"{_relative(path)} (the notes are not the last statement)")
    assert problems == []


def test_every_source_file_has_its_test_file_in_the_mirrored_place() -> None:
    """tests/ mirrors src/: `a/b/name.py` is tested by `tests/a/b/test_name.py`."""
    missing = []
    for path in _sources():
        if path.name == "__init__.py" or path.name in ROOT_FILES:
            continue
        expected = TESTS / path.relative_to(PACKAGE).parent / f"test_{path.stem}.py"
        if not expected.is_file():
            missing.append(expected.relative_to(TESTS).as_posix())
    assert missing == []


def test_every_test_file_belongs_to_a_source_file() -> None:
    """The other direction: no test file is left behind after its source was renamed or removed."""
    known = {
        (TESTS / path.relative_to(PACKAGE).parent / f"test_{path.stem}.py").relative_to(TESTS).as_posix()
        for path in _sources()
    }
    extra_by_design = {"test_public_api.py", "test_architecture.py"}
    leftovers = [
        path.relative_to(TESTS).as_posix()
        for path in sorted(TESTS.rglob("test_*.py"))
        if path.relative_to(TESTS).as_posix() not in known
        and path.relative_to(TESTS).as_posix() not in extra_by_design
        and path.relative_to(TESTS).parts[0] != "integration"
    ]
    assert leftovers == []
