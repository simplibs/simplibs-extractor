def is_key_part(value: str) -> bool:
    """Check whether a value can be one half of a profile key (`system` or `name`).

    Args:
        value: The candidate (`"python"`, `"code-clean"`).

    Returns:
        True for a non-blank string without surrounding whitespace that
        contains no `/`, `,` or whitespace; False for anything else.
    """

    # 1. Only a string can be a key part
    if not isinstance(value, str):
        return False

    # 2. Not blank and not padded
    if not value or value != value.strip():
        return False

    # 3. No separator the key syntax or the CLI list uses, no inner whitespace
    return not any(char in "/," or char.isspace() for char in value)


_DESIGN_NOTES = """
# is_key_part — Characters a Key Must Not Contain

## Purpose
A key is written `system/name` and several keys travel in one CLI argument
separated by commas. A `/` or `,` inside a part would make the key
ambiguous, and whitespace would not survive a command line.
"""
