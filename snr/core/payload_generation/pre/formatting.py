"""
Format the partitions on the host
"""
import os

from snr.core.core import context
from snr.core.payload_generation import common
from snr.core.util import common_utils, programs

__all__ = (
    "format_host",
)


def format_host(ctx: context.Context) -> bool:
    """Format partitions on the host

    Args:
        ctx: Context

    Returns:
        Whatever operation was successful or not
    """
    common_utils.print_debug("Formatting partitions")
    for index, tool, flags in (
        ("2", "mkfs.vfat", ("-F32",)),
        ("3", "mkfs.ext4", ("-F", "-L", "Rootfs",
         f"-Eroot_owner={os.getuid()}:{os.getgid()}"))
    ):
        part = ctx.construct_partition_path(index)
        tool_wrapper = programs.program_wrapper_factory(tool)(
            sudo=not common.is_user_disk_admin(),
            stdout=programs.PIPE,
            stderr=programs.STDOUT)
        errorcode = tool_wrapper.invoke_and_wait(None,
                                                 *flags,
                                                 part)
        if errorcode != 0:
            assert tool_wrapper.stdout is not None
            common_utils.print_debug(
                f"Command's output: {tool_wrapper.stdout.read()}")
            return common.clean_and_exit(ctx, "Formatting failed", True)
    return True
