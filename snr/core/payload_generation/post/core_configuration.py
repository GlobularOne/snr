"""
Configure snr core on the host
"""

import configparser

from snr.core.core import context
from snr.core.util import common_utils

__all__ = (
    "configure_core",
)


def configure_core(ctx: context.Context, verbosity: str) -> bool:
    """Configure snr core on the host

    Args:
        ctx: Context
        verbosity (str): Verbosity level
    """
    common_utils.print_debug("Configuring snr core on the host")
    # Ensure these directories exist
    for directory in [
            "root/.config/snr",
            "root/.cache/snr",
            "root/.local/state/snr",
            "root/.local/share/snr"]:
        common_utils.print_debug(
            f"Creating directory on the host: {directory}")
        ctx.makedirs(directory, exist_ok=True)
    config_parser = configparser.ConfigParser()
    data = {
        "main": {
            "verbose": False,
            "quiet": False,
            "debug": False,
        }
    }
    match verbosity:
        case "verbose":
            data["main"]["verbose"] = True
        case "quiet":
            data["main"]["quiet"] = True
        case "debug":
            data["main"]["verbose"] = True
            data["main"]["debug"] = True
        case "normal":
            pass
        case _:
            common_utils.print_error("Unknown verbosity mode")
            return False

    config_parser.read_dict(data)
    common_utils.print_debug("Writing configuration file to host rootfs")
    with common_utils.rootfs_open(ctx, "root/.config/snr/main.conf", "w") as stream:
        config_parser.write(stream)
    return True
