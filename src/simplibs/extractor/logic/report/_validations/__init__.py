from .raise_chars_per_token_error import raise_chars_per_token_error


_DESIGN_NOTES = """
# report/_validations — Private Diagnostics of the Report Phase

Plain imports only.

## Internal Components Registry

| Component                    | Type     | Description                                        |
| :--------------------------- | :------- | :------------------------------------------------- |
| `raise_chars_per_token_error`| Function | `chars_per_token` is zero or negative.             |
"""
