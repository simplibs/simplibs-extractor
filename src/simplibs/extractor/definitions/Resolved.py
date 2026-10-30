from dataclasses import dataclass
# Inners
from .ExtractionConfig import ExtractionConfig
from .Profile import Profile


@dataclass(frozen=True, slots=True)
class Resolved:
    """A configuration with every default filled in.

    Attributes:
        config: The config with a normalized `source` and a concrete `target`.
        profile: The profile object (never a key or `None`).
        format: The output format that will actually be used.
    """

    config: ExtractionConfig
    profile: Profile
    format: str


_DESIGN_NOTES = """
# Resolved — After the Defaults, Before the Work

## Purpose
Every later phase can rely on a normalized source, a concrete target, a real
profile and a known format, without repeating the `None` checks.
"""
