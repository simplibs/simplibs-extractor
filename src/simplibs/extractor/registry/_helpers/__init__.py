from .GENERIC_ALL import GENERIC_ALL
from .LANGUAGE_REGISTRY import LANGUAGE_REGISTRY
from .PROFILE_REGISTRY import PROFILE_REGISTRY
from .RENDERER_REGISTRY import RENDERER_REGISTRY


_DESIGN_NOTES = """
# registry/_helpers — Private State of the Registry

Plain imports only.

## Internal Components Registry

| Component           | Type       | Description                                      |
| :------------------ | :--------- | :----------------------------------------------- |
| `GENERIC_ALL`       | Profile    | The built-in profile `generic/all`.              |
| `LANGUAGE_REGISTRY` | Dictionary | Registered fence languages by suffix.            |
| `PROFILE_REGISTRY`  | Dictionary | Registered profiles by key.                      |
| `RENDERER_REGISTRY` | Dictionary | Registered renderers by format name.             |
"""
