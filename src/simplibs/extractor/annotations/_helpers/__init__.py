from .is_output_format import is_output_format


_DESIGN_NOTES = """
# annotations/_helpers — Private Helpers of the Annotations

Plain imports only. Used by the annotations of this folder, not exported
from the package root.

## Internal Components Registry

| Component          | Type     | Description                                              |
| :----------------- | :------- | :------------------------------------------------------- |
| `is_output_format` | Function | Validates whether a value has the shape of a format name. |
"""
