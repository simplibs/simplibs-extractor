import sys
from collections.abc import Sequence
from simplibs.cli import report_failures, resolve_verbosity
from simplibs.exception import SimpleError
from simplibs.logger import SimpleLogger
from simplibs.style import set_styles_enabled
# Outers
from ..logic import extract_many
from ..plugins import load_plugins
from ..scripts._helpers import print_result
# Inners
from ._helpers import describe_result, print_error
from .build_configs import build_configs
from .build_parser import build_parser
from .collect_dry_run import collect_dry_run
from .collect_profile_keys import collect_profile_keys
from .collect_source import collect_source
from .handle_list_options import handle_list_options
from .normalize_positionals import normalize_positionals
from .run_init import run_init


def run_cli(argv: Sequence[str] | None = None) -> int:
    """The `simplibs-extractor` command.

    Args:
        argv: The arguments without the program name; `None` reads `sys.argv`.

    Returns:
        The exit code: `0` everything succeeded, `1` some extraction failed or
        selected nothing, `2` the command was refused before anything ran.
        (`--help` and syntax errors of the arguments exit through `argparse`.)
    """
    arguments = list(sys.argv[1:] if argv is None else argv)

    # 1. Installed add-ons first: their profiles and formats belong in the parser's choices
    loaded, failed = load_plugins()

    # 2. A subcommand has its own parser
    if arguments[:1] == ["init"]:
        return run_init(arguments[1:])

    # 3. Parse, then sort the positional words into their roles
    args = normalize_positionals(build_parser().parse_args(arguments))
    if args.no_color:
        set_styles_enabled(False)
    logger = SimpleLogger(name="extractor", level=resolve_verbosity(quiet=args.quiet, verbose=args.verbose))
    for name, reason in failed.items():
        logger.log_warning("The add-on '%s' did not load: %s", name, reason)

    try:
        # 4. Questions about the registry end the command here
        if handle_list_options(args):
            return 0

        # 5. Everything that can be refused is checked before the first extraction runs
        asked = not args.profiles or args.source is None
        keys = collect_profile_keys(args)
        source = collect_source(args)
        configs = build_configs(args, keys, source, collect_dry_run(args, asked))
    except SimpleError as exc:
        print_error(exc)
        return 2

    # 6. Run all of them; a failed one is a result, not an exception
    results = extract_many(configs, logger=logger)
    if not args.quiet:
        for result in results:
            print_result(result)

    # 7. The failures once more, together, and the exit code
    everything_ok = report_failures(
        [(result, result.success) for result in results],
        describe=describe_result,
    )
    return 0 if everything_ok else 1


_DESIGN_NOTES = """
# run_cli — The Command, Start to Finish

## Purpose
Everything a person types ends here and comes out as an exit code that
scripts and CI can read: 0 fine, 1 something failed, 2 the command was wrong.

## Order
Plugins, then the parser (its choices depend on them), then the questions,
then all the checks, and only then the first extraction.

## Why Plugins Are Loaded Before the `init` Check
The profile choice of `init` lists the profiles of installed add-ons.

## What Is Caught
`SimpleError` only: the cards of this library and of `simplibs-cli`
(`CLI_NOT_INTERACTIVE`, ...) that mean "refused". A bug keeps its traceback.
`Ctrl+C` is not caught.

## Output
Summaries to standard output, refusals to standard error, progress through
the logger at the level `-q`, `-v` and `-vv` choose.
"""
