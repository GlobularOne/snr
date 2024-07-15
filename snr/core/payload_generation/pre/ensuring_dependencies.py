"""
Satisfy the reported payload dependencies
"""

from snr.core.core import context, options, common_paths
from snr.core.payload_generation import common
from snr.core.payload import payload
from snr.core.util import chroot_programs, common_utils

__all__ = (
    "ensure_dependencies",
)

ROOTFS_VERSION_PATCHES = [
    ("python3-deprecated", "python3-impacket", "python3-pycryptodome")  # v2
]


def ensure_dependencies(ctx: context.Context) -> bool:
    """Install dependencies of the payload

    Args:
        ctx: Context

    Returns:
        Whatever operation was successful or not
    """
    assert options.payload_module is not None
    p: payload.Payload = options.payload_module.payload  # pylint: disable=no-member
    # Check if the rootfs version is ok
    rootfs_version = getattr(
        p, "ROOTFS_VERSION", common_utils.get_rootfs_version())
    current_rootfs_version = common_utils.get_rootfs_version()
    if rootfs_version > common_paths.ROOTFS_CURRENT_VERSION:
        common_utils.print_error(
            f"Payload requires rootfs version {rootfs_version} however it is not known to us")
        return False
    if rootfs_version > current_rootfs_version:
        # We need to patch it up
        common_utils.print_info(
            f"Payload requires rootfs version {rootfs_version} but the current version is {current_rootfs_version}. Patching up!")
        for i in range(current_rootfs_version - 1, rootfs_version):
            p.DEPENDENCIES = (*p.DEPENDENCIES, *ROOTFS_VERSION_PATCHES[i])
    if len(p.DEPENDENCIES) != 0:
        common_utils.print_debug(
            "Installing dependencies of the payload:" +
            ' '.join(p.DEPENDENCIES))
        apt_get = chroot_programs.apt_get_factory(ctx)(
            stdout=chroot_programs.PIPE,
            stderr=chroot_programs.STDOUT,
        )

        errorcode = apt_get.invoke_and_wait(None,
                                            *p.DEPENDENCIES,
                                            options={
                                                "quiet": "2"
                                            })
        if errorcode != 0:
            assert apt_get.stdout is not None
            common_utils.print_debug(
                f"Command's output: {apt_get.stdout.read()}")
            return common.clean_and_exit(ctx, "Installing dependencies of payload failed")
    else:
        common_utils.print_debug("Payload has no dependencies, nothing to do")
    return True
