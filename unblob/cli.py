#!/usr/bin/env python3
import sys
from pathlib import Path
from typing import Tuple

import click
from structlog import get_logger

from .logging import configure_logger, noformat
from .processing import DEFAULT_DEPTH, process_file
from .state import exit_code_var

logger = get_logger()


@click.command()
@click.argument(
    "files",
    nargs=-1,
    type=click.Path(path_type=Path, exists=True, resolve_path=True),
)
@click.option(
    "-e",
    "--extract-dir",
    "extract_root",
    type=click.Path(path_type=Path, dir_okay=True, file_okay=False, resolve_path=True),
    default=Path.cwd(),
    help="Extract the files to this directory. Will be created if doesn't exist.",
)
@click.option(
    "-d",
    "--depth",
    type=int,
    default=DEFAULT_DEPTH,
    help="Recursion depth. How deep should we extract containers.",
)
@click.option("-v", "--verbose", is_flag=True, help="Verbose mode, enable debug logs.")
def cli(files: Tuple[Path], extract_root: Path, depth: int, verbose: bool):
    configure_logger(verbose, extract_root)
    logger.info("Start processing files", count=noformat(len(files)))
    for path in files:
        root = path if path.is_dir() else path.parent
        process_file(root, path, extract_root, max_depth=depth)


def main():
    try:
        # Click argument parsing
        ctx = cli.make_context("unblob", sys.argv[1:])
    except click.ClickException as e:
        e.show()
        sys.exit(e.exit_code)
    except click.exceptions.Exit as e:
        sys.exit(e.exit_code)
    except Exception:
        logger.exception("Unhandled exception during unblob")
        sys.exit(1)

    try:
        with ctx:
            cli.invoke(ctx)
    except Exception:
        logger.exception("Unhandled exception during unblob")
        sys.exit(1)

    sys.exit(exit_code_var.get(0))


if __name__ == "__main__":
    main()