from .is_generated_file import is_generated_file
from .read_source import read_source


_DESIGN_NOTES = """
# logic/read — Phase 2: What Is in the Files

Plain imports, no `__all__`.

## Internal Components Registry

| Component           | Type     | Description                                                    |
| :------------------ | :------- | :------------------------------------------------------------- |
| `is_generated_file` | Function | Checks the head of a file for the library's marker.            |
| `read_source`       | Function | Reads one file, or returns a report that says why it stays out.|
"""
