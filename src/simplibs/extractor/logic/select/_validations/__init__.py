from .raise_missing_source_error import raise_missing_source_error
from .raise_source_not_found_error import raise_source_not_found_error
from .raise_unknown_parameter_error import raise_unknown_parameter_error


_DESIGN_NOTES = """
# logic/select/_validations — Private Diagnostics of Phase 1

Plain imports only.

## Internal Components Registry

| Component                       | Type     | Description                                         |
| :------------------------------ | :------- | :-------------------------------------------------- |
| `raise_missing_source_error`    | Function | No config and no `source` were given.               |
| `raise_source_not_found_error`  | Function | The source is not an existing directory.            |
| `raise_unknown_parameter_error` | Function | A parameter is not a field of the config.           |
"""
