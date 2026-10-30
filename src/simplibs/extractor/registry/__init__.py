from ._helpers import GENERIC_ALL
from .expand_profile_keys import expand_profile_keys
from .get_profile import get_profile
from .get_renderer import get_renderer
from .list_formats import list_formats
from .list_profiles import list_profiles
from .list_systems import list_systems
from .register_profile import register_profile
from .register_renderer import register_renderer


# The built-in profile exists as soon as the registry is imported
register_profile(GENERIC_ALL, replace_existing=True)


_DESIGN_NOTES = """
# registry — Profiles and Renderers by Name

Plain imports, no `__all__`. The only side effect of importing this package
is the registration of the built-in profile `generic/all`.

## Internal Components Registry

| Component             | Type     | Description                                                  |
| :-------------------- | :------- | :----------------------------------------------------------- |
| `expand_profile_keys` | Function | Turns typed names into full `system/name` keys.              |
| `get_profile`         | Function | Returns a profile by key or raises `NotFoundError`.          |
| `get_renderer`        | Function | Returns a renderer by format name or raises `ParamError`.    |
| `list_formats`        | Function | Lists the registered output formats.                         |
| `list_profiles`       | Function | Lists the registered profiles, optionally of one system.     |
| `list_systems`        | Function | Lists the systems that have a profile.                       |
| `register_profile`    | Function | Registers a profile under its key.                           |
| `register_renderer`   | Function | Registers a renderer under a format name.                    |

## `replace_existing=True` for the Built-In
Re-importing or reloading the package must not fail on its own profile.
"""
