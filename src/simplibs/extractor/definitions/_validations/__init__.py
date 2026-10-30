from .raise_profile_key_part_error import raise_profile_key_part_error
from .raise_profile_output_name_error import raise_profile_output_name_error
from .raise_profile_steps_key_error import raise_profile_steps_key_error


_DESIGN_NOTES = """
# definitions/_validations — Private Diagnostics of the Definitions

Plain imports only. Every function raises one `ParamError` and returns nothing.

## Internal Components Registry

| Component                       | Type     | Description                                            |
| :------------------------------ | :------- | :----------------------------------------------------- |
| `raise_profile_key_part_error`  | Function | `system` or `name` cannot be a part of a profile key.  |
| `raise_profile_output_name_error` | Function | The output name is not a portable file name.         |
| `raise_profile_steps_key_error` | Function | A key of the steps mapping can never match a file.     |
"""
