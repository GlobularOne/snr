"""
Module containing utility functions to install snr's library onto the target
"""
import os
import os.path
import pathlib
import shutil

from snr.core.core import context
from snr.core.util import common_utils

__all__ = (
    "SNR_CORE_DIR", "DIST_PACKAGES_DIR",
    "install_snr_core_lib"
)

# Path to the currently installed snr core's root
SNR_CORE_DIR = pathlib.Path(__file__).parents[2]


def DIST_PACKAGES_DIR(ctx: context.Context) -> str:  # pylint: disable=invalid-name
    """Return the path to the dist-packages directory
     
    Args:
        ctx: The context to use for obtaining the directory
    
    Returns:
        The path to the dist-packages
    """
    return ctx.join("lib", "python3", "dist-packages")


def install_snr_core_lib(ctx: context.Context) -> None:
    """Install snr core library onto target

    Args:
        ctx: context to install snr core library
    """
    common_utils.print_debug("Installing snr core library to target")
    os.makedirs(os.path.join(
        DIST_PACKAGES_DIR(ctx), "snr"), exist_ok=True)
    shutil.copytree(SNR_CORE_DIR, os.path.join(
        DIST_PACKAGES_DIR(ctx), "snr", "core"))
    common_utils.print_debug("Installed snr core library successfully")
