"""
Core and common utilities. If a function is found here 
and also in snr.core.core, it is advised to use the one here
"""
import contextlib
import os
import os.path
import pdb
import shutil
import sys
from shutil import get_terminal_size
from typing import IO, Any, Callable, NoReturn

import deprecated
import rich.console
import rich.pretty
import rich.traceback

from snr.core.core import common_paths, console, context, options
from snr.core.core.logging import (carriage_return, clear_screen, print_debug,
                                   print_error, print_fatal, print_info,
                                   print_ok, print_sys, print_warning)

__all__ = (
    "get_terminal_size", "carriage_return",
    "clear_screen", "print_debug",
    "print_error", "print_fatal",
    "print_info", "print_ok",
    "print_sys", "print_warning",
    "EXTERNAL_CALL_FAILURE", "bytes_to_str_repr",
    "remake_dir", "graceful_exit",
    "call_external_function", "rootfs_open",
    "rootfs_makedirs", "get_rootfs_version",
    "temp_chdir", "UserError"
)

# External function call failed
EXTERNAL_CALL_FAILURE = "\x01"


class UserError(Exception):
    """An error by the user, when used by commands, the command dispatch will catch it and report it as a message"""
    message: str

    def __init__(self, message: str):
        self.message = message

    def __str__(self) -> str:
        return self.message


def bytes_to_str_repr(value: bytes) -> str:
    """Convert bytes to their string representation (as you would use in a python code)


    Returns:
        string backslash escaped representation of input
    """
    return repr(value)[2:-1]


def remake_dir(path: str) -> None:
    """Remove and recreate a directory.

    Args:
        path_ Path to the directory
    """
    shutil.rmtree(path)
    os.mkdir(path)


def graceful_exit() -> NoReturn:
    """Gracefully exit the program
    """
    sys.exit(options.default_exit_code)


def handle_exception() -> None:
    """Handle an exception. If debug mode is on. It drops to a default shell.
    """
    rich_trb = rich.traceback.Traceback(show_locals=options.verbose)
    console.err_console.print(rich_trb)
    rich.pretty.install()
    if options.debug:
        print_ok("Dropping to a debug shell")
        pdb.post_mortem()  # pylint: disable=no-member


def call_external_function(func: Callable[..., Any], *args: object, **kwargs: object) -> Any:
    """Call an external function catching and reporting any exceptions

    Args:
        func Function to call. Must be a callable

    Returns:
      The return value of the called function, or if the call failed EXTERNAL_CALL_FAILURE.
      It is recommended to check call failure with `result is EXTERNAL_CALL_FAILURE` and not `==`
      because EXTERNAL_CALL_FAILURE is a value and can be returned by a possible function
    """
    try:
        return func(*args, **kwargs)
    except UserError as exc:
        print_error(exc.message)
        return 1
    except Exception:  # pylint: disable=broad-exception-caught
        print_debug("Calling external function failed")
        handle_exception()
        return EXTERNAL_CALL_FAILURE


def get_rootfs_version() -> int:
    """Get version of the current rootfs

    Returns:
        Version of the current rootfs
    """
    if not os.path.exists(common_paths.ROOTFS_ARCHIVE_VERSION_PATH):
        print_sys("Could not read version data, assuming version 1")
        return 1
    with open(common_paths.ROOTFS_ARCHIVE_VERSION_PATH, encoding="utf-8") as stream:
        data = stream.read()

    try:
        return int(data.strip().strip("\n"))
    except ValueError:
        print_sys("Invalid data found in rootfs archive version file")
        return 0


temp_chdir = contextlib.chdir  # pylint: disable=invalid-name
