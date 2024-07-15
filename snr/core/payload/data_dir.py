"""
/data directory support
"""
import os
import os.path
from typing import IO, Any

import deprecated

from snr.core.core import path_wrapper
from snr.core.payload import storage
from snr.core.util import programs

__all__ = (
    "data", "fix_data_dir",
    "data_open", "data_mkdir"
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


@deprecated.deprecated("Use data.open instead", version="1.1.0")
def data_open(file: str, mode: str = "r", buffering: int = -1, encoding: str | None = None) -> IO[Any]:
    """Open a file in the data directory

    Args:
        file: The name of the file to open.
        mode: The mode to open the file in.
        buffering: The buffering size in bytes.
        encoding: The encoding to use.

    Returns:
        file-like object
    """
    return data.open(file, mode, buffering, encoding)


@deprecated.deprecated("Use data.mkdir instead", version="1.1.0")
def data_mkdir(dir_path: str, mode: int = 511) -> None:
    """Create a directory if it doesn't exist
    Args:
        path: Path to the directory to create
        mode: Permissions to set for the directory
    """
    return data.mkdir(dir_path, mode)


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
