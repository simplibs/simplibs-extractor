from .estimate_tokens import estimate_tokens
from .format_summary import format_summary


_DESIGN_NOTES = """
# logic/report — Phase 6: Say What Happened

Plain imports, no `__all__`.

## Internal Components Registry

| Component         | Type     | Description                                          |
| :---------------- | :------- | :--------------------------------------------------- |
| `estimate_tokens` | Function | A rough token count of a text.                       |
| `format_summary`  | Function | Readable text from an `ExtractionResult`.            |
"""
