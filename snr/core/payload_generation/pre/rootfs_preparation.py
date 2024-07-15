"""
Prepare rootfs for payload generation
"""
import os
import tarfile
import tempfile

from snr.core.core import common_paths, context, options
from snr.core.payload_generation import common
from snr.core.util import common_utils, programs

__all__ = (
    "prepare_rootfs",
)


def prepare_rootfs(ctx: context.Context) -> bool:
    """Prepare rootfs for payload generation.

    Args:
        ctx: Context

    Returns:
        Whatever operation was successful or not
    """
    common_utils.print_info("Preparing for payload generation")
    common_utils.print_debug("Unpacking rootfs image")
    root_directory = tempfile.mkdtemp(prefix="snr")
    mount = programs.Mount(
        sudo=True,
        stdout=programs.PIPE,
        stderr=programs.STDOUT)
    errorcode = mount.invoke_and_wait(
        None, ctx.construct_partition_path(3), root_directory)

    if errorcode != 0:
        assert mount.stdout is not None
        common_utils.print_debug("Mounting rootfs failed")
        common_utils.print_debug(
            f"Command's output: {mount.stdout.read()}")
        return common.clean_and_exit(ctx, "Copying rootfs to target failed", True)
    common_utils.print_debug(f"Rootfs is mounted at: {root_directory}")
    if not os.access(root_directory, os.W_OK):
        return common.clean_and_exit(ctx, "Rootfs mount point is not writable")
    ctx.to_level_3(root_directory)
    common_utils.print_debug(
        f"Extracting rootfs {common_paths.ROOTFS_ARCHIVE_PATH} to {root_directory}")
    try:
        with tarfile.open(common_paths.ROOTFS_ARCHIVE_PATH, common_paths.ROOTFS_ARCHIVE_FORMAT) as tar_stream:
            tar_stream.extractall(root_directory)
    except Exception as exc:  # pylint: disable=broad-exception-caught
        return common.clean_and_exit(ctx, f"Unpacking rootfs image failed ({exc})")
    for directory in ["bin", "lib", "var", "root"]:
        if not ctx.exists(directory):
            return common.clean_and_exit(ctx, "Archive did not extract correctly", True, True)
    common_utils.print_debug("Preparing rootfs")
    common_utils.print_debug("Writing hostname")
    with common_utils.rootfs_open(ctx, "etc/hostname", "w") as stream:
        stream.write(options.default_hostname + "\n")
    common_utils.print_debug("Writing dns configuration")
    with common_utils.rootfs_open(ctx, "etc/resolv.conf", "w") as stream:
        stream.write(f"nameserver {options.default_primary_nameserver}\n"
                     f"nameserver {options.default_secondary_nameserver}\n"
                     )
    return True
