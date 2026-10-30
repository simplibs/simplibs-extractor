from typing import Any, NoReturn
from simplibs.exception import ParamError


def raise_profile_key_part_error(part_name: str, value: Any) -> NoReturn:
    """Raise ParamError when `system` or `name` of a profile cannot be a part of a key.

    Args:
        part_name: Which half was rejected (`"system"` or `"name"`).
        value: The rejected value.
    """

    # 1. What a valid part looks like; the fix is built from it
    expected = f"a non-blank {part_name} without '/', ',' or whitespace"

    # 2. Raise structured ParamError wrapping a ValueError
    raise ParamError(
        error_name="EXTRACTOR_PROFILE_INVALID",
        label=f"profile {part_name}",
        value=value,
        problem=f"The {part_name} {value!r} cannot be a part of a profile key.",
        expected=expected,
        how_to_fix=f"Provide {expected}.",
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_profile_key_part_error — Half of a Key That Cannot Exist

## Purpose
A key is written `system/name` and several keys travel in one CLI argument
separated by commas, so neither half may contain `/`, `,` or whitespace.
"""
