from .cli import run_cli


_DESIGN_NOTES = """
# __main__ — `python -m simplibs.extractor`

The same command as the console script `simplibs-extractor`, for
environments where the script's folder is not on the path.
"""

if __name__ == "__main__":
    raise SystemExit(run_cli())
