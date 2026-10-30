from .Entry import Entry
from .ExtractionConfig import ExtractionConfig
from .ExtractionResult import ExtractionResult
from .FileReport import FileReport
from .Profile import Profile
from .Resolved import Resolved


_DESIGN_NOTES = """
# definitions — Data Objects of simplibs-extractor

Plain imports, no `__all__`. All of them are frozen dataclasses.

## Internal Components Registry

| Component          | Type      | Description                                           |
| :----------------- | :-------- | :---------------------------------------------------- |
| `Entry`            | Dataclass | One file ready to be rendered.                        |
| `ExtractionConfig` | Dataclass | Everything one run needs to know.                     |
| `ExtractionResult` | Dataclass | The outcome of one run; the source of every report.   |
| `FileReport`       | Dataclass | What happened to one file.                            |
| `Profile`          | Dataclass | A named set of rules and steps (`system/name`).       |
| `Resolved`         | Dataclass | A config with every default filled in.                |
"""
