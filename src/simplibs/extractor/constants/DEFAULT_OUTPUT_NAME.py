from typing import Final


DEFAULT_OUTPUT_NAME: Final[str] = "extraction.md"
"""The file name of an output when a profile does not choose its own."""


_DESIGN_NOTES = """
# DEFAULT_OUTPUT_NAME — A Name Every Profile Can Start From

## Purpose
The CLI's `-o` is a folder; the file name always comes from the profile, so
several profiles in one run produce several files instead of overwriting one.
"""
