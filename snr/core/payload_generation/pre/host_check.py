"""
Check target to ensure it can host a snr-generated rootfs
"""
import fcntl
import os
import os.path
import stat
import struct

from snr.core.core import context, options
from snr.core.util import common_utils

__all__ = (
    "check_host",
)


def check_host(ctx: context.Context) -> bool:
    """Check the host and print error if it is not a file or block device or doesn't meet the size requirements

    Args:
        ctx: Context

    Returns:
        Whatever operation was successful or not
    """
    if os.path.isfile(ctx.device_name):
        # Use os.path.getsize to get the size
        device_size = os.path.getsize(ctx.device_name)
        is_device = False
    elif stat.S_ISBLK(os.stat(ctx.device_name).st_mode):
        # Use ioctl to get the size
        buffer = b'\0' * 8
        with open(ctx.device_name, "rb") as stream:
            fcntl.ioctl(stream.fileno(), 0x80081272, buffer)
        device_size = struct.unpack("L", buffer)[0]
        is_device = True
    else:
        common_utils.print_error(
            f"'{ctx.device_name}' is not a file neither a device")
        return False
    if device_size < options.MINIMUM_TARGET_SIZE:
        common_utils.print_error(
            f"'{ctx.original_target}' is not at least"
            f"{options.MINIMUM_TARGET_SIZE / 1024 / 1024}MBs")
        return False
    ctx.to_level_1(device_size, is_device)
    return True
