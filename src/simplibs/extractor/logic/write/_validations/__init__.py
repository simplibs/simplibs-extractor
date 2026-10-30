from .raise_target_exists_error import raise_target_exists_error
from .raise_target_is_dir_error import raise_target_is_dir_error


_DESIGN_NOTES = """
# logic/write/_validations — Private Diagnostics of Phase 5

Plain imports only.

## Internal Components Registry

| Component                    | Type     | Description                                           |
| :--------------------------- | :------- | :---------------------------------------------------- |
| `raise_target_exists_error`  | Function | The output exists and the overwrite policy is 'error'. |
| `raise_target_is_dir_error`  | Function | The output path is an existing directory.             |
"""
