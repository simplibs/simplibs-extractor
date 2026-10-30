# Outers
from ..constants import SCRIPT_TEMPLATE


def render_script(file_name: str, profile_key: str) -> str:
    """Fill the script template.

    Args:
        file_name: The name the script will have (shown in its "Run it with" line).
        profile_key: The profile the script extracts with (`"python/code-clean"`).

    Returns:
        The source text of the script.
    """

    # 1. `{profile!r}` writes the key as a Python literal, so no key can break the code
    return SCRIPT_TEMPLATE.format(file_name=file_name, profile=profile_key)


_DESIGN_NOTES = """
# render_script — Template in, Text Out

## Purpose
Split from `generate_local_script` so the text of the script can be tested
(compiled, run) without touching the disk.
"""
