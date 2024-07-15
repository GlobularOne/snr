"""
Common paths used by snr and possibly by payloads
"""
import os.path
import pathlib

__all__ = (
    "USER_HOME_PATH", "XDG_DATA_HOME",
    "XDG_CONFIG_HOME", "XDG_CACHE_HOME",
    "DATA_PATH", "CONFIG_PATH",
    "STATE_PATH", "CACHE_PATH",
    "PAYLOAD_SET_PATH",
    "ROOTFS_ARCHIVE_BASE_PATH",
    "ROOTFS_ARCHIVE_PATH", "ROOTFS_ARCHIVE_FORMAT",
    "ROOTFS_ARCHIVE_EXTENSION",
    "format_rootfs_archive_path"
)

# User's home path
USER_HOME_PATH = os.path.expanduser("~")
# XDG data directory
XDG_DATA_HOME = os.environ.get(
    "XDG_DATA_HOME", os.path.join(USER_HOME_PATH, ".local", "share"))
# XDG config directory
XDG_CONFIG_HOME = os.environ.get(
    "XDG_CONFIG_HOME", os.path.join(USER_HOME_PATH, ".config"))
# XDG state directory
XDG_STATE_HOME = os.environ.get(
    "XDG_STATE_HOME", os.path.join(USER_HOME_PATH, ".local", "state"))
# XDG cache directory
XDG_CACHE_HOME = os.environ.get(
    "XDG_CACHE_HOME", os.path.join(USER_HOME_PATH, ".cache"))
# Snr's data path
DATA_PATH = os.path.join(XDG_DATA_HOME, "snr")
# Snr's configuration path
CONFIG_PATH = os.path.join(XDG_CONFIG_HOME, "snr")
# Snr's state path
STATE_PATH = os.path.join(XDG_STATE_HOME, "snr")
# Snr's cache path
CACHE_PATH = os.path.join(XDG_CACHE_HOME, "snr")

PAYLOAD_SET_PATH = str(pathlib.Path(__file__).parents[2] / "payloads")
# Snr's rootfs archive base path
ROOTFS_ARCHIVE_BASE_PATH = os.path.join(DATA_PATH, "jammy-{machine}")
# Current version of rootfs archive
ROOTFS_CURRENT_VERSION = 2
# The lowest version of supported rootfs archive
ROOTFS_MIN_VERSION = 2
# Snr's rootfs archive path
ROOTFS_ARCHIVE_PATH = ""
# The archive version
ROOTFS_ARCHIVE_VERSION_PATH = ""
# Snr's rootfs archive format
ROOTFS_ARCHIVE_FORMAT = "r:gz"
# Snr's rootfs archive file extension
ROOTFS_ARCHIVE_EXTENSION = ".tar.gz"


def format_rootfs_archive_path(machine: str) -> None:
    """Updates rootfs archive variables

    Args:
        machine: The machine architecture
    """
    global ROOTFS_ARCHIVE_BASE_PATH  # pylint: disable=global-statement
    global ROOTFS_ARCHIVE_PATH  # pylint: disable=global-statement
    global ROOTFS_ARCHIVE_VERSION_PATH  # pylint: disable=global-statement
    ROOTFS_ARCHIVE_BASE_PATH = ROOTFS_ARCHIVE_BASE_PATH.format(machine=machine)
    ROOTFS_ARCHIVE_PATH = ROOTFS_ARCHIVE_BASE_PATH + ROOTFS_ARCHIVE_EXTENSION
    ROOTFS_ARCHIVE_VERSION_PATH = ROOTFS_ARCHIVE_BASE_PATH + \
        ROOTFS_ARCHIVE_EXTENSION + ".version"
