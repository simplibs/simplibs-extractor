from .RunLog import RunLog
from .build_title import build_title
from .process_source import process_source


_DESIGN_NOTES = """
# run/_helpers — Private Helpers of the Run

Plain imports only.

## Internal Components Registry

| Component        | Type     | Description                                              |
| :--------------- | :------- | :------------------------------------------------------- |
| `RunLog`         | Class    | Adapter that writes progress to any logger, or to none.  |
| `build_title`    | Function | The configured or a generated heading of the output.     |
| `process_source` | Function | Reads one file and runs the steps; returns report and entry. |
"""
