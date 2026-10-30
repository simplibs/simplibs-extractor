from collections.abc import Mapping
from dataclasses import dataclass
from simplibs.path import is_valid_filename
from simplibs.rules import Rule
from simplibs.validate import validate_dataclass
# Outers
from ..annotations import OutputFormat, StepsSpec
from ..constants import DEFAULT_OUTPUT_NAME
# Inners
from ._helpers import is_key_part, is_suffix_key
from ._validations import (
    raise_profile_key_part_error,
    raise_profile_output_name_error,
    raise_profile_steps_key_error,
)


@validate_dataclass
@dataclass(frozen=True, slots=True)
class Profile:
    """A named set of selection rules and transformation steps.

    Registered under the key `"system/name"` (for example `"python/code-clean"`).

    Attributes:
        system: The family the profile belongs to (`"python"`, `"generic"`).
        name: The name inside the family (`"code-clean"`).
        description: One line shown by the listing commands.
        include: A rule on the relative path; only matching files are taken.
        exclude: A rule on the relative path; matching files are dropped.
        steps: How file text is transformed (see `StepsSpec`).
        output_name: The file name of the output.
        format: The output format.
    """

    system: str
    name: str
    description: str = ""
    include: Rule | None = None
    exclude: Rule | None = None
    steps: StepsSpec = None
    output_name: str = DEFAULT_OUTPUT_NAME
    format: OutputFormat = "markdown"

    def __post_init__(self) -> None:

        # 1. Both halves of the key must be usable in `system/name`
        for part_name, part in (("system", self.system), ("name", self.name)):
            if not is_key_part(part):
                raise_profile_key_part_error(part_name, part)

        # 2. The output name must be a portable file name
        if not is_valid_filename(self.output_name):
            raise_profile_output_name_error(self.output_name)

        # 3. A suffix mapping needs usable keys
        if isinstance(self.steps, Mapping):
            for suffix in self.steps:
                if not is_suffix_key(suffix):
                    raise_profile_steps_key_error(suffix)

    @property
    def key(self) -> str:
        """The registry key, `"system/name"`."""
        return f"{self.system}/{self.name}"


_DESIGN_NOTES = """
# Profile — Rules and Steps under One Name

## Purpose
Everything an add-on needs to teach the extractor a new kind of project:
which files, how to clean them, what the output is called.

## Rules Are Paths Only
`include` and `exclude` are evaluated on the path relative to the source
folder. They must therefore judge the path by its text (suffix, name,
folders). Anything that needs the disk (size, content) belongs to the read
phase.

## Two Layers of Checking
`@validate_dataclass` checks the type of every field (including the
`OutputFormat` shape) before anything is assigned. `__post_init__` adds what
a type cannot say: the characters of a key part, a portable output name, the
keys of a steps mapping. A bad profile fails when it is built, not at the
first run that happens to use it.

## Decorator Order
`@validate_dataclass` sits above `@dataclass`, as its README requires: it
wraps the `__init__` that `@dataclass` has just generated.

## Frozen
A registered profile is shared by every run; nobody may change it afterwards.
Create a new one with `dataclasses.replace`.
"""
