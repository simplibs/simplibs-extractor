from typing import Final


DEFAULT_SCRIPT_NAME: Final[str] = "extract_here.py"
"""The file name of a generated local script when only a folder is given."""


_DESIGN_NOTES = """
# DEFAULT_SCRIPT_NAME — "Put It In a Folder, Double-Click It"

## Purpose
`simplibs-extractor init my_project` needs a name for the script it creates.
The name says what the script does, and it is the one a person finds again
months later.
"""
