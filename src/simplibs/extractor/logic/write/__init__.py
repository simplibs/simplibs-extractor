from .write_output import write_output


_DESIGN_NOTES = """
# logic/write — Phase 5: Put It on the Disk

Plain imports, no `__all__`.

## Internal Components Registry

| Component      | Type     | Description                                                   |
| :------------- | :------- | :------------------------------------------------------------ |
| `write_output` | Function | Writes the output by the overwrite policy, or plans the write. |
"""
