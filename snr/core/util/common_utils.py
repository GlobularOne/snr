"""
Core and common utilities. If a function is found here 
and also in snr.core.core, it is advised to use the one here
"""
import os
import os.path
import pdb
import shutil
import sys
from shutil import get_terminal_size
from types import TracebackType
from typing import IO, Any, Callable, NoReturn

import rich.console
import rich.pretty
import rich.traceback


from snr.core.core import context, options, console
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
    "call_external_function", "rootfs_open"
)

# External function call failed
EXTERNAL_CALL_FAILURE = "\x01"


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
    except Exception:  # pylint: disable=broad-exception-caught
        print_debug("Calling external function failed")
        handle_exception()
        return EXTERNAL_CALL_FAILURE


def rootfs_makedirs(ctx: context.Context, path: str, mode: int = 511, exist_ok: bool = False) -> None:
    """makedirs but for rootfs

    Args:
        ctx: Context
        path: Path to directory to create
        mode: Directory permissions. Defaults to 511
        exist_ok: Whatever it's okay for directories to exist or not. Defaults to False
    """
    os.makedirs(os.path.join(
        ctx.root_directory, path
    ), mode=mode, exist_ok=exist_ok)


def rootfs_open(ctx: context.Context, file: str, mode: str = "r",
                buffering: int = -1, encoding: str | None = None) -> IO[Any]:
    """Open a file in rootfs

    Args:
        ctx: Context
        file: The file to open.
        mode: The mode to open the file with
        buffering: The buffering size to use
        encoding: The encoding to use. If None the default encoding will be used

    Returns:
        The opened stream
    """
    # pylint: disable=consider-using-with
    stream = open(os.path.join(
        ctx.root_directory, file), mode, buffering, encoding)

    def __enter__() -> IO[Any]:  # pylint: disable=unused-variable
        return stream

    def __exit__(exc_type: type[BaseException] | None,  # pylint: disable=unused-variable
                 exc_val: BaseException | None,
                 exc_tb: TracebackType | None) -> None:
        return stream.__exit__(exc_type, exc_val, exc_tb)
    return stream
