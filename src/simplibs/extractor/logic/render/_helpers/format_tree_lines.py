def format_tree_lines(node: dict, prefix: str = "") -> list[str]:
    """Draw a nested dictionary of names as the lines of a directory tree.

    Args:
        node: Names mapped to their children (an empty dictionary for a file).
        prefix: The indentation inherited from the parent levels.

    Returns:
        The lines, folders before files, each group sorted case-insensitively.
    """

    # 1. Folders first, then files; alphabetical inside each group
    items = sorted(node.items(), key=lambda item: (0 if item[1] else 1, item[0].lower()))

    # 2. Draw every item, descending into folders
    lines: list[str] = []
    for index, (name, children) in enumerate(items):
        is_last = index == len(items) - 1
        lines.append(prefix + ("└── " if is_last else "├── ") + name + ("/" if children else ""))
        if children:
            lines.extend(format_tree_lines(children, prefix + ("    " if is_last else "│   ")))

    return lines


_DESIGN_NOTES = """
# format_tree_lines — The Drawing Half of the Tree

## Purpose
Separated from `build_tree` so that building the nested structure and
drawing it are two small, separately testable steps.

## Folders First
The order a file manager shows, which is what people expect from a tree.
"""
