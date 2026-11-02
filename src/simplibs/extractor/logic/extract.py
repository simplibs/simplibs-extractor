import time
from typing import Any
# Outers
from ..definitions import Entry, ExtractionConfig, ExtractionResult, FileReport
from ..registry import get_renderer
# Inners
from .render import RenderContext
from .report import estimate_tokens
from .select import resolve_config, select_sources
from .write import write_output
from ._helpers import RunLog, build_title, process_source


def extract(
    config: ExtractionConfig | None = None,
    *,
    logger: Any = None,
    **overrides: Any,
) -> ExtractionResult:
    """Run one extraction: select, read, transform, render, write, report.

    Takes a ready `ExtractionConfig`, plain keyword values
    (`extract(source=".", profile="python/code-clean")`), or both: the
    keywords then change a copy of the config.

    Args:
        config: A ready config, or `None` to build one from the keywords.
        logger: Where progress goes: a `SimpleLogger`, a standard `Logger`, or `None` for silence.
        **overrides: Fields of `ExtractionConfig` to set or to change.

    Returns:
        The result: per-file reports, sizes, the output path, and whether
        anything was written. Problems with single files are inside it.

    Raises:
        ParamError, NotFoundError: For a configuration that cannot run (unknown
            field, missing source, unknown profile or format).
        AlreadyExistsError, StateError, AccessError, ConversionError: From the
            write, when the output cannot be written.
    """
    started = time.perf_counter()
    log = RunLog(logger)

    # 1. Resolve and check everything that can fail before any file is touched
    plan = resolve_config(config, overrides)
    cfg, profile = plan.config, plan.profile
    log.info("Extracting %s with profile %s", cfg.source, profile.key)

    # 2. Select
    paths = select_sources(plan)
    log.info("Selected %d file(s)", len(paths))

    # 3. Read and transform, file by file; a bad file is reported, never fatal
    reports: list[FileReport] = []
    entries: list[Entry] = []
    for path in paths:
        report, entry = process_source(path, plan)
        if entry is not None:
            entries.append(entry)
        reports.append(report)
        if report.status in ("error", "partial"):
            log.warning("%s: %s (%s)", report.relative, report.status, report.reason)
        else:
            log.debug("%s: %s%s", report.relative, report.status, f" ({report.reason})" if report.reason else "")

    # 4. Render and write — only when there is something to write
    rendered = ""
    written = False
    target = cfg.target
    if entries:
        context = RenderContext(build_title(cfg), cfg.source, profile.key, cfg.add_tree)
        rendered = get_renderer(plan.format)(entries, context)
        target = write_output(cfg.target, rendered, cfg.overwrite, cfg.dry_run)
        written = not cfg.dry_run
    else:
        log.warning("Nothing to extract - no file was written")

    # 5. Report
    result = ExtractionResult(
        config=cfg,
        profile_key=profile.key,
        target=target,
        written=written,
        dry_run=cfg.dry_run,
        files=tuple(reports),
        bytes_in=sum(r.bytes_in for r in reports if r.status in ("ok", "partial")),
        bytes_out=len(rendered.encode("utf-8")),
        tokens_estimate=estimate_tokens(rendered),
        duration=time.perf_counter() - started,
    )
    (log.success if result.success else log.warning)("Done: %s", target)
    return result


_DESIGN_NOTES = """
# extract — Six Phases in Order

## Purpose
The public entry point of the library. It only wires the phases together;
each phase is a function with its own tests.

## Two Kinds of Failure
A configuration that cannot run raises before any file is touched. A single
file that cannot be read or transformed is a line in the result. A write that
fails (or is refused by the `error` policy) raises, because then there is no
output at all.

## Nothing Is Printed
Progress goes to the logger the caller passed, if any; the outcome goes into
the result. The CLI turns the result into a summary and an exit code.

## Not Wrapped in `@validate_call`
The inputs arrive as keyword overrides; they become an `ExtractionConfig`,
whose own `@validate_dataclass` checks every field. A second layer in front
would only check the same values twice.

## An Empty Selection Writes Nothing
`success` is then False. A file with only a title would hide a wrong filter.
"""
