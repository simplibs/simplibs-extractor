from .load_plugins import load_plugins


_DESIGN_NOTES = """
# plugins — Finding Add-Ons

Plain imports, no `__all__`.

## Internal Components Registry

| Component      | Type     | Description                                               |
| :------------- | :------- | :-------------------------------------------------------- |
| `load_plugins` | Function | Runs the registration function of every installed add-on. |
"""
