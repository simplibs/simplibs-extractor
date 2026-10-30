from .extract_here import extract_here
from .generate_local_script import generate_local_script
from .render_script import render_script


_DESIGN_NOTES = """
# scripts — The Extractor Inside a Project Folder

Plain imports, no `__all__`.

## Internal Components Registry

| Component               | Type     | Description                                                |
| :---------------------- | :------- | :--------------------------------------------------------- |
| `extract_here`          | Function | Extracts the folder of a script into a file next to it.    |
| `generate_local_script` | Function | Writes a ready-to-run local script.                        |
| `render_script`         | Function | Fills the script template; no disk access.                 |
"""
