from .is_key_part import is_key_part
from .is_suffix_key import is_suffix_key


_DESIGN_NOTES = """
# definitions/_helpers — Private Helpers of the Definitions

Plain imports only.

## Internal Components Registry

| Component       | Type     | Description                                              |
| :-------------- | :------- | :------------------------------------------------------- |
| `is_key_part`   | Function | Validates one half (`system` or `name`) of a profile key. |
| `is_suffix_key` | Function | Validates a key of a `suffix -> Action` mapping.          |
"""
