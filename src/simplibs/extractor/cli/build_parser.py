import argparse
from pathlib import Path
from typing import get_args
# Outers
from ..annotations import OverwritePolicy
from ..registry import list_formats


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser of `simplibs-extractor`.

    Returns:
        The parser. Every positional argument is optional: what is missing
        is asked for, or refused when there is nobody to ask.
    """

    # 1. Description and the three optional positionals
    parser = argparse.ArgumentParser(
        prog="simplibs-extractor",
        description="Extract the files of a folder into one document.",
        epilog="Also: simplibs-extractor init [FOLDER]  (writes a local extract_here.py script).",
    )
    parser.add_argument("system", nargs="?", help="a system (python), or full profile keys (python/code-clean)")
    parser.add_argument("profiles", nargs="?", help="profile names, comma separated (code-clean,data-all)")
    parser.add_argument("source", nargs="?", type=Path, help="the folder to extract from")

    # 2. Where and how the output is written
    parser.add_argument("-o", "--output", type=Path, metavar="FOLDER", help="output FOLDER (default: the source)")
    parser.add_argument("--format", choices=list_formats(), help="output format (default: the profile's)")
    parser.add_argument("--overwrite", choices=get_args(OverwritePolicy), default="overwrite",
                        help="what to do when the output exists (default: overwrite)")
    parser.add_argument("--no-tree", dest="add_tree", action="store_false", default=True,
                        help="leave the directory tree out of the output")
    parser.add_argument("--dry-run", action="store_true", default=None,
                        help="plan and report, write nothing")

    # 3. How much to say
    parser.add_argument("-q", "--quiet", action="store_true", help="only errors")
    parser.add_argument("-v", "--verbose", action="count", default=0, help="more detail (-vv for everything)")
    parser.add_argument("--no-color", action="store_true", help="plain text, no colors")

    # 4. Questions about the registry, answered without extracting
    parser.add_argument("--list-systems", action="store_true", help="list the registered systems and exit")
    parser.add_argument("--list-profiles", metavar="SYSTEM", help="list the profiles of a system and exit")

    return parser


_DESIGN_NOTES = """
# build_parser — The Whole Command Line in One Place

## Purpose
The syntax of the tool is read here and nowhere else.

## Choices Come From the Registry
`--format` lists the registered renderers and `--overwrite` the values of
`OverwritePolicy`, so a new format or policy appears in the help without a
change in the parser. Plugins must therefore be loaded before the parser is
built.

## `--dry-run` Defaults to `None`
"Not given" is different from "no": the wizard asks about a dry run only when
the flag was not given.

## `-o` Is a Folder
The file name comes from the profile, so several profiles in one run write
several files side by side.
"""
