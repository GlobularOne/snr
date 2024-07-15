"""
Install GRUB for both UEFI and BIOS boot on the host
"""
from snr.core.core import context
from snr.core.payload_generation import common
from snr.core.util import chroot_programs, common_utils, programs

__all__ = (
    "install_grub",
)


def install_grub(ctx: context.Context) -> bool:
    """Install GRUB for both UEFI and BIOS boot on the target

    Args:
        ctx: Context

    Returns:
        Whatever operation was successful or not
    """
    boot_mount_info = (
        (ctx.construct_partition_path(2), "boot/efi"),
    )
    for src, dest in boot_mount_info:
        common_utils.print_debug(f"Mounting /{dest}")
        mount = programs.Mount(sudo=True)

        errorcode = mount.invoke_and_wait(None,
                                          src,
                                          ctx.join(dest))
        if errorcode != 0:
            assert mount.stdout is not None
            common_utils.print_debug(
                f"Command's output: {mount.stdout.read()}")
            return common.clean_and_exit(ctx, "Preparing to install grub failed", True, True)

    common.bind_required_rootfs_dirs(ctx)
    common_utils.print_debug("Installing UEFI grub")
    grub_install = chroot_programs.grub_install_factory(ctx)(
        stdout=chroot_programs.PIPE,
        stderr=chroot_programs.STDOUT,
        sudo=True)
    errorcode = grub_install.invoke_and_wait(None,
                                             ctx.device_name,
                                             options={
                                                 "uefi-secure-boot": None,
                                                 "removable": None
                                             })
    if errorcode != 0:
        assert grub_install.stdout is not None
        common_utils.print_debug(
            f"Command's output: {grub_install.stdout.read()}")
        common.unbind_required_rootfs_dirs(ctx)
        return common.clean_and_exit(ctx, "Installing grub failed", True, True)

    common_utils.print_debug("Install BIOS grub")
    grub_install = chroot_programs.grub_install_factory(ctx)(
        stdout=chroot_programs.PIPE,
        stderr=chroot_programs.STDOUT,
        sudo=True)
    errorcode = grub_install.invoke_and_wait(None,
                                             ctx.device_name,
                                             options={"target": "i386-pc"})
    if errorcode != 0:
        common.unbind_required_rootfs_dirs(ctx)
        assert grub_install.stdout is not None
        common_utils.print_debug(
            f"Command's output: {grub_install.stdout.read()}")
        return common.clean_and_exit(ctx, "Installing grub failed", True, True)
    common.unbind_required_rootfs_dirs(ctx)
    return True
