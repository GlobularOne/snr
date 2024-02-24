"""
Module containing atexit callbacks
"""
import atexit as _atexit
import os as _os

from libsnr.util.coloring import RESET
from libsnr.util.common_utils import print_info as _print_info

_old_root = _os.getcwd()


def restore_cwd():
    """
    Restore CWD to what it was once this file was imported
    """
    _print_info("Restoring CWD...")
    _os.chdir(_old_root)


def reset_terminal():
    """
    Restore terminal color and style states
    """
    print(RESET)


def register_atexit_callbacks():
    """
    Register all atexit callbacks
    """
    _atexit.register(reset_terminal)
    _atexit.register(restore_cwd)


def unregister_atexit_callbacks():
    """
    Unregister all atexit callbacks
    """
    _atexit.unregister(reset_terminal)
    _atexit.unregister(restore_cwd)
