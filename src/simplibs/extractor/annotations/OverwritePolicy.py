from typing import Literal


OverwritePolicy = Literal["overwrite", "unique", "backup", "error"]
"""What happens when the output file already exists.

`"overwrite"` replaces it atomically, `"unique"` writes `name (1).ext` next to
it, `"backup"` keeps the old file as a backup and then replaces it, `"error"`
refuses to write.
"""


_DESIGN_NOTES = """
# OverwritePolicy — Four Answers to "It Already Exists"

## Purpose
The old code knew only `"error"`. The ecosystem already has the building
blocks for the other three (`SafeFileWriter`, `make_unique_path`,
`backup_file`), so the policy is a closed, readable choice.

## Default
`"overwrite"` — an extractor is re-run constantly and its output is
generated, never hand-edited. The write itself is atomic.
"""
