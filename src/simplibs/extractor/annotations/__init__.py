from .FileStatus import FileStatus
from .OutputFormat import OutputFormat
from .OverwritePolicy import OverwritePolicy
from .StepsSpec import StepsSpec


_DESIGN_NOTES = """
# annotations — Shared Types of simplibs-extractor

Plain imports, no `__all__` (the package root decides what is public).
`PathLike` and `ByteCount` are not redefined here — they come from
`simplibs.path` and `simplibs.file`.

## Internal Components Registry

| Component         | Type            | Description                                             |
| :---------------- | :-------------- | :------------------------------------------------------ |
| `FileStatus`      | Literal Type    | Outcome of one file: `ok`, `partial`, `skipped`, `error`. |
| `OutputFormat`    | Annotated Type  | The name of an output format.                           |
| `OverwritePolicy` | Literal Type    | What to do when the output exists.                      |
| `StepsSpec`       | Union Type      | One action, a suffix -> action mapping, or nothing.     |

## Changed in Batch 2
`is_output_format` is no longer re-exported: `Profile` is now checked by
`@validate_dataclass`, which reads the `OutputFormat` annotation itself.
"""
