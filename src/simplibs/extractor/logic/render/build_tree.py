from collections.abc import Sequence
# Inners
from ._helpers import format_tree_lines


def build_tree(paths: Sequence[str]) -> str:
    """Draw a directory tree from relative paths.

    Args:
        paths: Relative paths with `/` separators (`"src/a.py"`).

    Returns:
        The tree as text, one line per name. Empty for no paths.
    """

    # 1. Fold the paths into nested dictionaries: {"src": {"a.py": {}}}
    root: dict = {}
    for path in paths:
        node = root
        for part in path.split("/"):
            node = node.setdefault(part, {})

    # 2. Draw it
    return "\n".join(format_tree_lines(root))


_DESIGN_NOTES = """
# build_tree — An Overview Before the Contents

## Purpose
A reader (or a model) sees the shape of the project before the first file.

## Built From the Selected Files Only
Not from the disk: the tree shows exactly what is in the output, never a
folder whose files were all skipped.
"""
