"""
/data directory support
"""
import os
import os.path

from snr.core.core import path_wrapper
from snr.core.payload import storage
from snr.core.util import programs

__all__ = (
    "data", "fix_data_dir",
)

data = path_wrapper.PathWrapperBase("/data")


def fix_data_dir() -> None:
    """Ensure a writable /data directory.
    If the rootfs is mounted writable, it does nothing.
    Otherwise it mounts a temporary in-ram filesystem on /data
    """
    try:
        os.mkdir("/data/_fix_data_dir_test")
    except PermissionError:
        programs.Mount().invoke_and_wait(None, "tmpfs",
                                         "/data", options={"t": "tmpfs"})
    else:
        os.rmdir("/data/_fix_data_dir_test")


def wrap_data_path_for_block(info: storage.BlockInfo) -> path_wrapper.PathWrapperBase:
    """Wrap a new path for a specific block

    Args:
        info: Information on the block

    Returns:
        Wrapped path specific to that block
    """
    if info.uuid is not None:
        identifier = info.uuid
    else:
        identifier = info.path.replace("/", ".")[1:]
    data.makedirs(identifier, exist_ok=True)
    return data.wrap(identifier)
