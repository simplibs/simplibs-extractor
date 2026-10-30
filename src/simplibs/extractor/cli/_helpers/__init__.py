from .describe_result import describe_result
from .is_profile_reference import is_profile_reference
from .print_error import print_error
from .profile_options import profile_options
from .system_options import system_options


_DESIGN_NOTES = """
# cli/_helpers — Private Helpers of the Command Line

Plain imports only.

## Internal Components Registry

| Component              | Type     | Description                                              |
| :--------------------- | :------- | :------------------------------------------------------- |
| `describe_result`      | Function | One line saying why an extraction failed.                |
| `is_profile_reference` | Function | Whether a word is a registered system or profile keys.   |
| `print_error`          | Function | Prints an error card to standard error.                  |
| `profile_options`      | Function | `{name: description}` of one system's profiles.          |
| `system_options`       | Function | `{system: "N profile(s)"}` of every registered system.   |
"""
