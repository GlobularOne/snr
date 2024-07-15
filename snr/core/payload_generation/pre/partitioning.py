"""
Partition the host device
"""
import os.path
import time

from snr.core.core import context
from snr.core.payload_generation import common
from snr.core.util import common_utils, programs

__all__ = (
    "partition_host",
)


def partition_host(ctx: context.Context) -> bool:
    """Create partitions on the block device

    Args:
        ctx: Context

    Returns:
        Whatever operation was successful or not
    """
    common_utils.print_debug("Partitioning target")
    common_utils.print_debug("Clearing partition data on disk")
    use_sudo = False
    if not os.access(ctx.original_target, os.W_OK):
        use_sudo = True
    errorcode = programs.Sgdisk(
        sudo=use_sudo,
        stdout=programs.PIPE,
        stderr=programs.STDOUT).invoke_and_wait(None, "-z", ctx.original_target)
    if errorcode != 0:
        return common.clean_and_exit(ctx, "Partitioning failed")
    common_utils.print_debug("Partitioning disk")
    sgdisk_options: dict[str, str] = {}
    for index, part_info in enumerate((
        ("+1M", "1:ef02", "BIOS Boot"),
        ("+128M", "2:ef00", "ESP"),
        ("-0", "3:8300", "Rootfs")
    )):
        size, typecode, name = part_info
        common_utils.print_debug(f"Creating a partition for {name}")
        sgdisk_options.clear()
        sgdisk_options["new"] = f"{index+1}::{size}"
        sgdisk_options["typecode"] = typecode
        sgdisk_options["change-name"] = name
        sgdisk = programs.Sgdisk(
            sudo=use_sudo,
            stdout=programs.PIPE,
            stderr=programs.STDOUT)

        errorcode = sgdisk.invoke_and_wait(
            None, ctx.original_target, options=sgdisk_options)
        if errorcode != 0:
            assert sgdisk.stdout is not None
            common_utils.print_debug(
                f"Command's output: {sgdisk.stdout.read()}")
            return common.clean_and_exit(ctx, "Partitioning failed")
    part_prefix = ""
    if not ctx.is_device:
        common_utils.print_debug(
            "Original target is not a device, mounting it on loop")
        part_prefix = "p"
        # Setup a loop, we need proper partition access
        losetup = programs.Losetup(
            sudo=not common.is_user_disk_admin(),
            stdout=programs.PIPE,
            stderr=programs.STDOUT)
        errorcode = losetup.invoke_and_wait(None, ctx.device_name,
                                            options={
                                                "find": None,
                                                "show": None,
                                                "partscan": None})
        assert losetup.stdout is not None
        if errorcode != 0:
            common_utils.print_debug(
                f"Command's output: {losetup.stdout.read()}")
            return common.clean_and_exit(ctx, "Partitioning failed")
        ctx.device_name = losetup.stdout.read().strip().strip("\n")
    elif ctx.device_name.startswith("nvme"):
        part_prefix = "p"
    common_utils.print_debug("Giving kernel time to discover the partitions")
    time.sleep(1)
    common_utils.print_debug("Checking if all partitions exist")
    ctx.to_level_2(part_prefix)
    for i in range(1, 4):
        if not os.path.exists(ctx.construct_partition_path(i)):
            common_utils.print_debug(
                f"Partition {i} not found! ({ctx.construct_partition_path(i)})")
            return common.clean_and_exit(ctx, "Partitioning failed", True)
    return True
