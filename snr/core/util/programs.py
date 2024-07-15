"""
ProgramWrapper derivatives for common tools
"""

from snr.core.util.program_wrapper import (DEVNULL, PIPE, STDOUT,
                                           SubprocessError,
                                           program_wrapper_factory)

__all__ = (
    "DEVNULL", "PIPE",
    "STDOUT", "SubprocessError",
    "program_wrapper_factory",
    "Mount", "Umount",
    "Sync", "Vgscan",
    "Lvscan", "Cryptsetup",
    "Losetup", "Sgdisk",
    "Partprobe", "Chmod",
    "Lsblk", "Chown"
)

Debootstrap = program_wrapper_factory("debootstrap")
Mount = program_wrapper_factory("mount")
Umount = program_wrapper_factory("umount")
Sync = program_wrapper_factory("sync")
Vgscan = program_wrapper_factory("vgscan")
Lvscan = program_wrapper_factory("lvscan")
Pvchange = program_wrapper_factory("pvchange")
Cryptsetup = program_wrapper_factory("cryptsetup")
Losetup = program_wrapper_factory("losetup")
Sgdisk = program_wrapper_factory("sgdisk")
Partprobe = program_wrapper_factory("partprobe")
Chmod = program_wrapper_factory("chmod")
Lsblk = program_wrapper_factory("lsblk")
Chown = program_wrapper_factory("chown")
