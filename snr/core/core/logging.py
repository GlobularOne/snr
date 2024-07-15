"""
Utility functions to log output to the screen and the log file,
@note Do not use the print_sys function in anywhere with the exception of the snr cli code.
"""
import io
import os.path
import re
import sys
import time
from typing import TextIO

import rich.console
import rich.pretty

from snr.core.core import common_paths, options

__all__ = (
    "SYS", "DEBUG",
    "INFO", "OK",
    "WARNING", "ERROR",
    "carriage_return", "clear_screen",
    "print_sys", "print_debug",
    "print_info", "print_ok",
    "print_warning", "print_error",
    "print_fatal"
)

LOG_FILE_PATH: str = os.path.join(common_paths.STATE_PATH, "main.log")
ERROR_LOG_FILE_PATH: str = os.path.join(common_paths.STATE_PATH, "errors.log")

LOG_FILE_STREAM: io.TextIOWrapper
ERROR_LOG_FILE_STREAM: io.TextIOWrapper

# System message symbol
SYS = "-->"
# Debug message symbol
DEBUG = "[[magenta].[/magenta]]"
# Informational message symbol
INFO = "[[blue]![/blue]]"
# Successful message symbol
OK = "[[green]+[/green]]"
# Warning message symbol
WARNING = "[[yellow]*[/yellow]]"
# Error message symbol
ERROR = "[[red]-[/red]]"

_ANSI_ESCAPE = re.compile(r'\x1b\[[0-9;]*m')


def carriage_return() -> None:
    """Return to the previous line.
    """
    sys.stdout.write('\r')


def clear_screen() -> None:
    """Clears the screen.
    """
    print("\x1b[H\x1b[2J\x1b[3J")


def _stringize(obj: object) -> str:
    if isinstance(obj, rich.pretty.Pretty):
        return _ANSI_ESCAPE.sub('', rich.pretty.pretty_repr(obj._object).strip())  # pylint: disable=protected-access
    return str(obj)


def _print_raw(*args: object, sep: str = ' ',
               end: str = '\n', file: TextIO = sys.stderr, flush: bool = False) -> None:

    s = sep.join(map(_stringize, args))
    if file == sys.stderr:
        console = rich.console.Console()
    else:
        console = rich.console.Console(file=file)
    if s.startswith(INFO):
        if not options.quiet:
            console.print(s, sep=sep, end=end)
            if flush:
                console.file.flush()
    elif s.startswith(DEBUG):
        if options.verbose:
            console.print(s, sep=sep, end=end)
            if flush:
                console.file.flush()
    else:
        console.print(s, sep=sep, end=end)
        if flush:
            console.file.flush()
    LOG_FILE_STREAM.write(
        f"[{int(time.time())}] {_ANSI_ESCAPE.sub('', s)}")
    LOG_FILE_STREAM.flush()
    if str(args[0]).startswith(ERROR):
        ERROR_LOG_FILE_STREAM.write(
            f"[{int(time.time())}] {_ANSI_ESCAPE.sub('', s)}")
        ERROR_LOG_FILE_STREAM.flush()


def print_sys(*args: object, sep: str = ' ',
              end: str = '\n', file: TextIO = sys.stderr, flush: bool = False) -> None:
    """Print a message to the log file with the system symbol.

    Args:
        args: The arguments to print.
        sep: The separator between the arguments.
        end: The end of the message.
        file: The file to print to.
        flush: Whether to flush the output.
    """
    _print_raw(SYS, *args, sep=sep, end=end, file=file, flush=flush)


def print_debug(*args: object, sep: str = ' ',
                end: str = '\n', file: TextIO = sys.stderr, flush: bool = False) -> None:
    """Print a message to the log file with the debug symbol, but only if on verbose mode.

    Args:
        args: The arguments to print.
        sep: The separator between the arguments.
        end: The end of the message.
        file: The file to print to.
        flush: Whether to flush the output.
    """
    _print_raw(DEBUG, *args, sep=sep, end=end, file=file, flush=flush)


def print_info(*args: object, sep: str = ' ',
               end: str = '\n', file: TextIO = sys.stderr, flush: bool = False) -> None:
    """Print a message to the log file with the info symbol, but only if on quiet mode.

    Args:
        args: The arguments to print.
        sep: The separator between the arguments.
        end: The end of the message.
        file: The file to print to.
        flush: Whether to flush the output.
    """
    _print_raw(INFO, *args, sep=sep, end=end, file=file, flush=flush)


def print_ok(*args: object, sep: str = ' ',
             end: str = '\n', file: TextIO = sys.stderr, flush: bool = False) -> None:
    """Print a message to the log file with the ok symbol.

    Args:
        args: The arguments to print.
        sep: The separator between the arguments.
        end: The end of the message.
        file: The file to print to.
        flush: Whether to flush the output.
    """
    _print_raw(OK, *args, sep=sep, end=end, file=file, flush=flush)


def print_warning(*args: object, sep: str = ' ',
                  end: str = '\n', file: TextIO = sys.stderr, flush: bool = False) -> None:
    """Print a message to the log file with the warning symbol.

    Args:
        args: The arguments to print.
        sep: The separator between the arguments.
        end: The end of the message.
        file: The file to print to.
        flush: Whether to flush the output.
    """
    _print_raw(WARNING, *args, sep=sep, end=end, file=file, flush=flush)


def print_error(*args: object, sep: str = ' ',
                end: str = '\n', file: TextIO = sys.stderr, flush: bool = False) -> None:
    """Print a message to the log file with the error symbol.

    Args:
        args: The arguments to print.
        sep: The separator between the arguments.
        end: The end of the message.
        file: The file to print to.
        flush: Whether to flush the output.
    """
    _print_raw(ERROR, *args, sep=sep, end=end, file=file, flush=flush)


def print_fatal(*args: object, sep: str = ' ',
                end: str = '\n', file: TextIO = sys.stderr, flush: bool = False) -> None:
    """Print a message to the log file with the error symbol, exiting afterwards.
    Exit code is taken from snr.core.options.default_exit_code

    Args:
        args: The arguments to print.
        sep: The separator between the arguments.
        end: The end of the message.
        file: The file to print to.
        flush: Whether to flush the output.
    """
    _print_raw(ERROR, *args, sep=sep, end=end, file=file, flush=flush)
    if not options.debug:
        raise SystemExit(options.default_exit_code)
    raise RuntimeError(sep.join(map(str, args)))


def _try_open_log_files() -> None:
    global LOG_FILE_STREAM  # pylint: disable=global-statement
    global ERROR_LOG_FILE_STREAM  # pylint: disable=global-statement

    if hasattr(_try_open_log_files, "has_already_done"):
        return

    try:
        for file in (LOG_FILE_PATH, ERROR_LOG_FILE_PATH):
            if not os.path.exists(LOG_FILE_PATH):
                with open(file, "w", encoding="utf-8") as _:
                    pass
        LOG_FILE_STREAM = open(LOG_FILE_PATH,  # pylint: disable=consider-using-with
                               "a", encoding="utf-8")
        ERROR_LOG_FILE_STREAM = open(ERROR_LOG_FILE_PATH,  # pylint: disable=consider-using-with
                                     "a", encoding="utf-8")
    except OSError as exc:
        # We cannot fail because the logger cannot open a file
        # Assume a readonly filesystem and use an IO wrapper
        LOG_FILE_STREAM = io.TextIOWrapper(io.BytesIO())
        ERROR_LOG_FILE_STREAM = io.TextIOWrapper(io.BytesIO())

        print_sys(
            f"Failed to open log file: Using in-memory buffer instead ({exc})")
    setattr(_try_open_log_files, "has_already_done", True)
    print_debug("Logger started")


_try_open_log_files()
