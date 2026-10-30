from .build_configs import build_configs
from .build_parser import build_parser
from .collect_dry_run import collect_dry_run
from .collect_profile_keys import collect_profile_keys
from .collect_source import collect_source
from .handle_list_options import handle_list_options
from .normalize_positionals import normalize_positionals
from .run_cli import run_cli
from .run_init import run_init


_DESIGN_NOTES = """
# cli — The Command Line of simplibs-extractor

Plain imports, no `__all__`. `run_cli` is the console-script entry point
(`simplibs-extractor = simplibs.extractor.cli:run_cli`); it returns the exit
code, which a console script passes to `sys.exit`.

## Internal Components Registry

| Component               | Type     | Description                                              |
| :---------------------- | :------- | :------------------------------------------------------- |
| `build_configs`         | Function | One config per profile key.                              |
| `build_parser`          | Function | The argument parser.                                     |
| `collect_dry_run`       | Function | The dry-run flag, asked for only inside the wizard.      |
| `collect_profile_keys`  | Function | Profile keys from the command line or from questions.    |
| `collect_source`        | Function | The source folder from the command line or a question.   |
| `handle_list_options`   | Function | Answers `--list-systems` and `--list-profiles`.          |
| `normalize_positionals` | Function | Sorts the three positional words into their roles.       |
| `run_cli`               | Function | The command; returns the exit code.                      |
| `run_init`              | Function | The `init` subcommand.                                   |
"""
