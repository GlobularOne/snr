"""
Add the finishing touch to the host rootfs
"""
import json
import os.path

from snr.core.core import context
from snr.core.payload_generation import common
from snr.core.util import chroot_programs, common_utils, programs

__all__ = (
    "finish_host",
)

FSTAB_FORMAT = """\
# Snr-generated fstab
# <file system>  <mount point>  <type>  <options>          <dump>  <pass>
UUID={root_uuid} /              ext4    errors=remount-ro  0       1
UUID={esp_uuid}  /boot/efi      vfat    umask=0077         0       0
"""


def finish_host(ctx: context.Context) -> bool:  # pylint: disable=too-many-return-statements
    """Add the finishing touch to the host rootfs

    Args:
        ctx: Context

    Returns:
        Whatever operation was successful or not
    """
    common_utils.print_debug("Adding the finishing touch to the target")
    lsblk = programs.Lsblk(stdout=programs.PIPE, stderr=programs.STDOUT)
    errorcode = lsblk.invoke_and_wait(None, ctx.device_name, options={
                                      "J": None, "o": "NAME,UUID"})
    assert lsblk.stdout is not None
    if errorcode != 0:
        common_utils.print_debug(f"Command's output: {lsblk.stdout.read()}")
        return common.clean_and_exit(ctx, "Discovering partition UUIDs failed", True, True)
    parts_info = json.load(lsblk.stdout)["blockdevices"][0]["children"]
    esp_part_name = os.path.basename(ctx.construct_partition_path(2))
    root_part_name = os.path.basename(ctx.construct_partition_path(3))
    esp_uuid = None
    root_uuid = None
    for part_info in parts_info:
        if part_info["name"] == esp_part_name:
            esp_uuid = part_info["uuid"]
        if part_info["name"] == root_part_name:
            root_uuid = part_info["uuid"]
    if esp_uuid is None:
        return common.clean_and_exit(ctx, "ESP UUID not found!", True, True)
    if root_uuid is None:
        return common.clean_and_exit(ctx, "Rootfs UUID not found!", True, True)
    with common_utils.rootfs_open(ctx, "etc/fstab", "w", encoding="ascii") as stream:
        stream.write(FSTAB_FORMAT.format(
            esp_uuid=esp_uuid, root_uuid=root_uuid))
    common_utils.print_debug("Generating initramfs")
    update_initramfs = chroot_programs.update_initramfs_factory(ctx)(
        stdout=chroot_programs.PIPE,
        stderr=chroot_programs.STDOUT,
        sudo=True)
    errorcode = update_initramfs.invoke_and_wait(None, options={
        "c": None, "k": "all",
    })
    if errorcode != 0:
        assert update_initramfs.stdout is not None
        common_utils.print_debug(
            f"Command's output: {update_initramfs.stdout.read()}")
        return common.clean_and_exit(ctx, "Generating initramfs failed", True, True)
    common_utils.print_debug("Updating grub configuration")
    with common_utils.rootfs_open(ctx, "etc/default/grub", "r",
                                  encoding="ascii") as stream:
        grub_cfg = stream.read()
        grub_cfg = grub_cfg.replace("GRUB_TIMEOUT=5", "GRUB_TIMEOUT=0")
        grub_cfg = grub_cfg.replace(
            "#GRUB_DISABLE_RECOVERY=\"true\"", "GRUB_DISABLE_RECOVERY=\"true\"")
    with common_utils.rootfs_open(ctx, "etc/default/grub", "w",
                                  encoding="ascii") as stream:
        stream.write(grub_cfg)

    common.bind_required_rootfs_dirs(ctx)
    update_grub = chroot_programs.update_grub_factory(ctx)(
        stdout=chroot_programs.PIPE,
        stderr=chroot_programs.STDOUT,
        sudo=True)
    errorcode = update_grub.invoke_and_wait(None)
    if errorcode != 0:
        assert update_grub.stdout is not None
        common_utils.print_debug(
            f"Command's output: {update_grub.stdout.read()}")
        return common.clean_and_exit(ctx, "Updating grub configuration failed")

    common_utils.print_debug("Clearing root password")
    passwd = chroot_programs.passwd_factory(ctx)(
        stdout=chroot_programs.PIPE,
        stderr=chroot_programs.STDOUT,
        sudo=True)

    errorcode = passwd.invoke_and_wait(None, "root",
                                       options={
                                           "d": None,
                                           "q": None
                                       })

    if errorcode != 0:
        assert passwd.stdout is not None
        common_utils.print_debug(
            f"Command's output: {passwd.stdout.read()}")
        common.unbind_required_rootfs_dirs(ctx)
        return common.clean_and_exit(ctx, "Clearing root password failed")
    common.unbind_required_rootfs_dirs(ctx)
    common_utils.print_debug("Fixing up owner on the rootfs")
    chown = programs.Chown(sudo=True)
    errorcode = chown.invoke_and_wait(None, "root:root", ctx.root_directory, options={
        "recursive": None,
    })
    if errorcode != 0:
        return common.clean_and_exit(ctx, "Preparing to install grub failed", True, True)
    return True
