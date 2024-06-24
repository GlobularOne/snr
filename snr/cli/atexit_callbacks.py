"""
Standard snr shell atexit callbacks
"""
import atexit
import os

from snr.core.util import common_utils

_old_root = os.getcwd()

__all__ = (
    "restore_cwd",
    "register_atexit_callbacks", "unregister_atexit_callbacks"
)


def restore_cwd() -> None:
    """
    Restore CWD to what it was once this file was imported
    """
    common_utils.print_info("Restoring CWD...")
    os.chdir(_old_root)


def register_atexit_callbacks() -> None:
    """
    Register all atexit callbacks
    """
    atexit.register(restore_cwd)


def unregister_atexit_callbacks() -> None:
    """
    Unregister all atexit callbacks
    """
    atexit.unregister(restore_cwd)
