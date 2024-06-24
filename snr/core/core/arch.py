"""
Receive the machine architecture generally and for a few packages
"""
import platform

from snr.core.core import options

__all__ = (
    "get_arch", "get_kernel_arch",
    "get_grub_arch"
)


def get_arch() -> str:
    """Get the architecture of the system based on the platform machine or specified option.

    Returns:
        If options.arch is defined, it returns that, otherwise it returns
        the output of platform.machine()
    """
    if hasattr(options, "arch"):
        return options.arch
    machine = platform.machine()
    if machine in ("i386", "i486", "i586", "i686"):
        return "i386"
    return machine


def get_kernel_arch() -> str:
    """Get the architecture in a way that debian kernels are branded by architecture

    Returns:
        Architecture of the machine, in a way that
        linux-image-{get_kernel_arch()} is a valid debian package 
    """
    # Output of uname -i and uname -o is unknown in many situations
    # (Which also makes platform.processor unreliable)
    # So translate them based on architecture
    arch = get_arch()
    if arch == "x86_64":
        return "amd64"
    return arch


def get_grub_arch() -> str:
    """Get the architecture in a way that debian grub packages are branded by architecture
    Returns:
        Architecture of the machine, in a way that grub-efi-{grub_arch} is a valid debian package 
    """
    arch = get_kernel_arch()
    if arch == "i386":
        return "ia32"
    return arch
