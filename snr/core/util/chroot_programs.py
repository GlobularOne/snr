"""
ChrootProgramWrapper derivatives for common tools
"""

from snr.core.util.chroot_program_wrapper import (
    DEVNULL, PIPE, STDOUT, SubprocessError, chroot_program_wrapper_factory)

__all__ = (
    "DEVNULL", "PIPE",
    "STDOUT", "SubprocessError",
    "chroot_program_wrapper_factory",
    "update_initramfs_factory", "update_grub_factory",
    "passwd_factory", "grub_install_factory",
    "apt_get_factory", "chown_factory"
)

update_initramfs_factory = chroot_program_wrapper_factory("update-initramfs")
update_grub_factory = chroot_program_wrapper_factory("update-grub")
passwd_factory = chroot_program_wrapper_factory("passwd")
grub_install_factory = chroot_program_wrapper_factory("grub-install")
apt_get_factory = chroot_program_wrapper_factory("apt-get")
chown_factory = chroot_program_wrapper_factory("chown")
