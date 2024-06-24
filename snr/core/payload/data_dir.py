"""
/data directory support
"""
import os
import os.path
from types import TracebackType
from typing import IO, Any

from snr.core.util import programs

__all__ = (
    "fix_data_dir", "data_open",
    "data_mkdir"
)


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
    stream = open(os.path.join("/data", file), mode, buffering,  # pylint: disable=consider-using-with
                  encoding)

    def __enter__() -> IO[Any]:  # pylint: disable=unused-variable
        return stream.__enter__()

    def __exit__(exc_type: type[BaseException] | None,  # pylint: disable=unused-variable
                 exc_val: BaseException | None,
                 exc_tb: TracebackType | None) -> None:  # pylint: disable=unused-variable
        return stream.__exit__(exc_type, exc_val, exc_tb)
    return stream


def data_mkdir(dir_path: str, mode: int = 511) -> None:
    """Create a directory if it doesn't exist
    Args:
        path: Path to the directory to create
        mode: Permissions to set for the directory
    """
    os.mkdir(dir_path, mode=mode)
