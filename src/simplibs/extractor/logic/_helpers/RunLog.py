from typing import Any


class RunLog:
    """A thin adapter that lets the run write progress to any logger, or to none.

    Accepts a `simplibs.logger.SimpleLogger` (`log_debug`, `log_info`,
    `log_success`, `log_warning`), a standard `logging.Logger` (`debug`,
    `info`, `warning`; success is written as info), or `None`.
    """

    __slots__ = ("_logger",)

    def __init__(self, logger: Any = None) -> None:
        self._logger = logger

    def debug(self, message: str, *args: Any) -> None:
        self._emit("debug", "debug", message, args)

    def info(self, message: str, *args: Any) -> None:
        self._emit("info", "info", message, args)

    def success(self, message: str, *args: Any) -> None:
        self._emit("success", "info", message, args)

    def warning(self, message: str, *args: Any) -> None:
        self._emit("warning", "warning", message, args)

    def _emit(self, name: str, standard_name: str, message: str, args: tuple) -> None:
        """Write through `log_<name>` if the logger has it, else through the standard method."""

        # 1. No logger, no output
        if self._logger is None:
            return

        # 2. The simplibs method first, the standard `logging` method as the fallback
        method = getattr(self._logger, f"log_{name}", None) or getattr(self._logger, standard_name)
        method(message, *args)


_DESIGN_NOTES = """
# RunLog — Progress Without a Hard Dependency on One Logger

## Purpose
The run reports what it does ("Selected 12 files", "x.py: error ..."). Where
that goes is the caller's decision: the CLI passes a `SimpleLogger`, a script
may pass nothing, an application may pass its own `logging.Logger`.

## Why an Adapter and Not an Import
`extract()` must not create a logger or print by itself, and it must not force
`simplibs-logger` on code that already has logging. Anything with the usual
methods works.

## `%`-Style Arguments
Messages are passed with their arguments, never pre-formatted, so a disabled
level costs no formatting.
"""
