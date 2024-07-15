"""
Common utilities for payload generation
"""
import grp
import os
import pwd
import shutil
from typing import Literal

from snr.core.core import context, options
from snr.core.util import common_utils, programs

__all__ = (
    "is_user_disk_admin", "bind_required_rootfs_dirs",
    "unbind_required_rootfs_dirs", "clean_on_success",
    "clean_and_exit"
)


def is_user_disk_admin() -> bool:
    """Is the user a disk administrator
    Being a disk administrator means either being in `disk` group, or being root

    Returns:
        Whatever the current user is a disk admin or not
    """
    if os.getuid() == 0:
        return True
    username = pwd.getpwuid(os.getuid()).pw_name
    try:
        for group in grp.getgrall():
            if username in group.gr_mem and group.gr_name == "disk":
                return True
        return False
    except KeyError:
        return False


def bind_required_rootfs_dirs(ctx: context.Context) -> None:
    """Bind required directories for a chroot environment

    Args:
        ctx: Context
    """
    for node, check_measure in [("dev", "dev/random"), ("sys", "sys/kernel"), ("proc", "proc/self")]:
        if ctx.exists(check_measure):
            common_utils.print_debug(f"/{node} is already mounted")
            continue
        common_utils.print_debug(f"Mounting /{node}")
        ctx.makedirs(node, exist_ok=True)
        mount = programs.Mount(sudo=True)

        errorcode = mount.invoke_and_wait(None,
                                          "-B",
                                          f"/{node}",
                                          ctx.join(node))
        if errorcode != 0:
            assert mount.stdout is not None
            common_utils.print_debug(
                f"Command's output: {mount.stdout.read()}")
            clean_and_exit(
                ctx, "Binding required rootfs directories for a chroot failed", True, True)


def unbind_required_rootfs_dirs(ctx: context.Context) -> None:
    """Unbind required directories for a chroot environment, as well as boot/efi

    Args:
        ctx: Context
    """
    for node in ["sys", "dev", "proc", "boot/efi"]:
        common_utils.print_debug(f"Unmounting /{node}")
        umount = programs.Umount(sudo=True,
                                 stdout=programs.PIPE,
                                 stderr=programs.STDOUT)

        errorcode = umount.invoke_and_wait(None,
                                           os.path.join(
                                               ctx.root_directory, node),
                                           options={})
        if errorcode != 0:
            assert umount.stdout is not None
            output = umount.stdout.read()
            if "not mounted" not in output:
                common_utils.print_debug(
                    f"Command's output: {output}")


def clean_on_success(ctx: context.Context,
                     unmount_loop: bool = False,
                     clear_root_directory: bool = False) -> Literal[True]:
    """Clean up after success.

    Args:
        ctx: Context
        unmount_loop: Whether or not to unmount the loop device. Defaults to False
        clear_root_directory: Whether or not to clear root_directory. Defaults to False

    Returns:
        Always returns True
    """
    if not ctx.is_device and unmount_loop:
        common_utils.print_debug("Unmounting rootfs filesystem")
        umount = programs.Umount(
            sudo=True,
            stdout=programs.DEVNULL,
            stderr=programs.DEVNULL)
        umount.invoke_and_wait(None, ctx.root_directory)
        common_utils.print_debug("Deleting loop")
        losetup = programs.Losetup(
            sudo=not is_user_disk_admin(),
            stdout=programs.DEVNULL,
            stderr=programs.DEVNULL)
        losetup.invoke_and_wait(None, ctx.device_name,
                                options={
                                    "detach": None
                                })
    if clear_root_directory and ctx.level >= 3:
        unbind_required_rootfs_dirs(ctx)
        common_utils.print_debug(
            "Changing file ownerships back to user for deletion")
        chroot = programs.Chown(sudo=True)
        chroot.invoke_and_wait(None, f"{os.getuid()}:{os.getgid()}", ctx.root_directory, options={
            "recursive": None,
        })
        common_utils.print_debug("Cleaning up root directory")
        shutil.rmtree(ctx.root_directory, ignore_errors=True)
    return True


def clean_and_exit(ctx: context.Context, message: str,
                   unmount_loop: bool = False, clear_root_directory: bool = False) -> Literal[False]:
    """Clean and exit with error

    Args:
        ctx: Context 
        message: error message to pass to clean_on_success
        unmount_loop: if True unmount the loop
        clear_root_directory: Whether or not to clear root_directory. Defaults to False

    Returns:
        Always return False
    """
    if not options.debug:
        clean_on_success(ctx, unmount_loop, clear_root_directory)
    else:
        # Still for safety reasons it's best to do this
        unbind_required_rootfs_dirs(ctx)
    common_utils.print_fatal(message)
    return False
