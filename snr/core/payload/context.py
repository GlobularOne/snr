"""
Context management utilities. Some snr functions require a context variable to work,
functions in this module help creating a context for a payload
"""

import os.path

from snr.core.core.context import Context
from snr.core.util import common_utils, programs

__all__ = (
    "create_context_for_mount_point", "require_context_for_mount_point",
    "Context"
)


def create_context_for_mount_point(mount_point: str) -> Context:
    """Create context for mount point

    Args:
        mount_point: Path to the mount point

    Returns:
        A Context instance for that mount point.
        The context is has level 3 but device_size is assumed 0.
        To get the size of the underlying device of a mountpoint,
        use the snr.core.payload.storage functions
    """
    mount = programs.Mount(stdout=programs.PIPE)
    mount.invoke_and_wait(None)
    assert mount.stdout is not None
    mtab_raw_data = mount.stdout.read()
    for line in mtab_raw_data.splitlines():
        source, _, dest, __ = line.split(maxsplit=3)
        if dest == mount_point:
            device = source
            break
    else:
        raise ValueError(f"'{mount_point}' is not a valid mount point")
    partitions_prefix = ""
    assert isinstance(device, str)
    if os.path.basename(device).startswith(("nvme", "loop")):
        partitions_prefix = "p"
    context = Context(device)
    context.to_level_1(0, True)
    context.to_level_2(partitions_prefix)
    context.to_level_3(mount_point)
    return context


def require_context_for_mount_point(mount_point: str) -> Context:
    """Get context for a mount point or exit

    Args:
        mount_point: Mount point to get the context for

    Raises:
        SystemExit: Could not find the mount point

    Returns:
        Context for the specified mount point
    """
    try:
        return create_context_for_mount_point(mount_point)
    except ValueError:
        common_utils.print_error(
            f"Creating context for '{mount_point}' failed")
        raise SystemExit(1) from None
