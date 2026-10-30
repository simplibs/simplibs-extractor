from .raise_duplicate_output_error import raise_duplicate_output_error
from .raise_list_unknown_system_error import raise_list_unknown_system_error
from .raise_output_is_file_error import raise_output_is_file_error
from .raise_too_many_positionals_error import raise_too_many_positionals_error
from .raise_unknown_system_error import raise_unknown_system_error


_DESIGN_NOTES = """
# cli/_validations — Private Diagnostics of the Command Line

Plain imports only. Every function raises one `ParamError` and returns nothing.

## Internal Components Registry

| Component                         | Type     | Description                                                   |
| :-------------------------------- | :------- | :------------------------------------------------------------ |
| `raise_duplicate_output_error`    | Function | Two profiles would write the same output file.                |
| `raise_list_unknown_system_error` | Function | `--list-profiles` names a system without profiles.            |
| `raise_output_is_file_error`      | Function | `-o` points to a file, not a folder.                          |
| `raise_too_many_positionals_error`| Function | Full profile keys were followed by two more words.            |
| `raise_unknown_system_error`      | Function | The system named (or chosen) has no registered profile.       |
"""
