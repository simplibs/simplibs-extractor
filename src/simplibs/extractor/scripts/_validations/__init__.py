from .raise_invalid_output_name_error import raise_invalid_output_name_error
from .raise_not_python_script_error import raise_not_python_script_error


_DESIGN_NOTES = """
# scripts/_validations — Private Diagnostics of the Scripts

Plain imports only.

## Internal Components Registry

| Component                         | Type     | Description                                          |
| :-------------------------------- | :------- | :--------------------------------------------------- |
| `raise_invalid_output_name_error` | Function | The output name is not a plain file name.            |
| `raise_not_python_script_error`   | Function | The script name does not end with `.py`.             |
"""
