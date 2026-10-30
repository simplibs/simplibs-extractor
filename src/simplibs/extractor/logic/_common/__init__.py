from .describe_failure import describe_failure


_DESIGN_NOTES = """
# logic/_common — Helpers Shared by Several Phases

Plain imports only. The phases of `logic/` do not import each other; what
two of them need lives here.

## Internal Components Registry

| Component          | Type     | Description                                      |
| :----------------- | :------- | :----------------------------------------------- |
| `describe_failure` | Function | One readable line for an exception in a report.  |
"""
