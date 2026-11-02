from .assert_profile_identity import assert_profile_identity
from .assert_profile_selection import assert_profile_selection
from .assert_profile_steps import assert_profile_steps


_DESIGN_NOTES = """
# testing/asserts — The Blades of `assert_profile`

Plain imports, no `__all__`. Each blade checks one area of a profile and can
be used alone; `assert_profile` calls them in order.

## Internal Components Registry

| Component                  | Type     | Description                                              |
| :------------------------- | :------- | :------------------------------------------------------- |
| `assert_profile_identity`  | Function | The key, the description, the output name and format.    |
| `assert_profile_selection` | Function | Which relative paths the `include` / `exclude` rules take. |
| `assert_profile_steps`     | Function | What the steps do to a text, suffix by suffix.            |
"""
