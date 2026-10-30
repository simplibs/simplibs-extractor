from .all_of import all_of
from .any_of import any_of
from .resolve_config import resolve_config
from .resolve_ignore_names import resolve_ignore_names
from .resolve_profile import resolve_profile
from .select_sources import select_sources


_DESIGN_NOTES = """
# logic/select — Phase 1: Which Files

Plain imports, no `__all__`.

## Internal Components Registry

| Component              | Type     | Description                                               |
| :--------------------- | :------- | :-------------------------------------------------------- |
| `all_of`               | Function | Combines rules with AND, ignoring `None`.                 |
| `any_of`               | Function | Combines rules with OR, ignoring `None`.                  |
| `resolve_config`       | Function | Fills in defaults and checks the config before the work.  |
| `resolve_ignore_names` | Function | The default or chosen names the scan skips.               |
| `resolve_profile`      | Function | Turns a profile, a key or `None` into a profile.          |
| `select_sources`       | Function | Collects the files an extraction takes.                   |
"""
