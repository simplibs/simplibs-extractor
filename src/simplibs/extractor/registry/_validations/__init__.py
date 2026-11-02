from .raise_language_exists_error import raise_language_exists_error
from .raise_language_name_error import raise_language_name_error
from .raise_language_suffix_error import raise_language_suffix_error
from .raise_missing_system_error import raise_missing_system_error
from .raise_no_profile_given_error import raise_no_profile_given_error
from .raise_profile_exists_error import raise_profile_exists_error
from .raise_profile_not_found_error import raise_profile_not_found_error
from .raise_renderer_exists_error import raise_renderer_exists_error
from .raise_unknown_renderer_error import raise_unknown_renderer_error


_DESIGN_NOTES = """
# registry/_validations — Private Diagnostics of the Registry

Plain imports only.

## Internal Components Registry

| Component                        | Type     | Description                                        |
| :------------------------------- | :------- | :------------------------------------------------- |
| `raise_language_exists_error`    | Function | The suffix already has a language.                 |
| `raise_language_name_error`      | Function | A language name cannot be written after a fence.   |
| `raise_language_suffix_error`    | Function | A suffix cannot be the key of a language.          |
| `raise_missing_system_error`     | Function | A profile name has no system and none was given.   |
| `raise_no_profile_given_error`   | Function | No profile name was given at all.                  |
| `raise_profile_exists_error`     | Function | A profile key is registered twice.                 |
| `raise_profile_not_found_error`  | Function | A profile key is not registered.                   |
| `raise_renderer_exists_error`    | Function | The format name already has a renderer.            |
| `raise_unknown_renderer_error`   | Function | No renderer has this format name.                  |
"""
