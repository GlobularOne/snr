"""
Utility functions to help with the storage.
Allows working with LVM and getting information on all and any disk or partition
"""
import contextlib
import copy
import json
import os
import tempfile
import time
from typing import Iterable, Literal, Any

from snr.core.core import path_wrapper
from snr.core.payload import context
from snr.core.util import common_utils, programs

__all__ = (
    "BlockInfoTypesType", "BlockInfo",
    "query_all_block_info", "query_all_partitions",
    "query_partition_info_by_path", "query_partition_info_by_uuid",
    "query_partition_info_by_name", "lvm_scan_all",
    "lvm_activate_all_vgs", "luks_is_partition_encrypted",
    "luks_open", "luks_close",
    "get_partition_root", "require_root_device",
    "setup", "handle_luks_partition",
    "MountedPartition", "mount_partition"
)

###############################################################################
# Block and partition support
###############################################################################

BlockInfoTypesType = Literal['part'] | Literal['crypt'] | Literal['loop'] | Literal['disk'] | Literal['rom']


class BlockInfo:
    """Info about a block device

    Attributes:
        name: Name of the block ("sda", "sda3", "nvme0np1", "loop1", etc)
        uuid: UUID of the block, can be None (loops, and disks don't have UUID)
        type: Either part, crypt, loop, disk or rom
        size: Size of the partition in bytes
        path: Absolute path to the block
        children: The children of the said block
          For a disk, the children are it's partitions
          For a loop, if mounted, the children are it's partitions
          For a partition, if it is an encrypted partition, it has a child (once it gets unlocked)
          A crypt does not have children
          Note that those above are normal cases,
          for example, a crypt technically can have children, if you encrypt a 
          partition twice for example
    """
    name: str
    uuid: str | None
    type: BlockInfoTypesType
    size: int
    path: str
    children: tuple['BlockInfo', ...]

    def __init__(self,
                 name: str, uuid: str | None,
                 type_: BlockInfoTypesType, size: int,
                 path: str, children: tuple['BlockInfo', ...] = ()):
        self.name = name
        self.uuid = uuid
        self.type = type_
        self.size = size
        self.path = path
        self.children = children if len(children) > 0 else ()

    def is_partition(self) -> bool:
        """Is the block a partition

        Returns:
            Whatever the block is a partition or not
        """
        return self.type == "part"

    def is_disk(self) -> bool:
        """Is the block a disk

        Returns:
            Whatever the block is a disk or not
        """
        return self.type == "disk"

    def is_crypt(self) -> bool:
        """Is the block an encrypted partition
        Note that the physical encrypted partition is a normal partition
        but the block that is created when the said partition is decrypted
        that block is crypt. The right way to determine if a partition is encrypted
        is to use luks_is_partition_encrypted

        Returns:
            Whatever the block is an encrypted partition or not
        """
        return self.type == "disk"

    def is_loop(self) -> bool:
        """Is the block a loop

        Returns:
            Whatever the block is a loop or not
        """
        return self.type == "loop"

    def is_rom(self) -> bool:
        """Is the block a rom

        Returns:
            Whatever the block is a rom or not
        """
        return self.type == "rom"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, (BlockInfo, str)):
            return NotImplemented

        if isinstance(other, str):
            if other.startswith("/"):
                # Compare the paths
                return self.path == other
            # Compare by uuid
            return self.uuid == other
        return self.path == other.path


def query_all_block_info() -> list[BlockInfo]:
    """Query block information for all block devices.
    Returns:
        A list of block devices
    """
    lsblk = programs.Lsblk(stdout=programs.PIPE)
    lsblk.invoke_and_wait(None,  options={
                          "J": None, "M": None, "b": None, "o": "NAME,UUID,TYPE,SIZE,PATH"})
    assert lsblk.stdout is not None
    block_devices_raw = json.load(lsblk.stdout)
    block_devices = []
    for block_device_raw in block_devices_raw["blockdevices"]:
        block_device = BlockInfo(block_device_raw["name"],
                                 block_device_raw["uuid"],
                                 block_device_raw["type"],
                                 block_device_raw["size"],
                                 block_device_raw["path"],
                                 tuple(block_device_raw["children"]))
        block_devices.append(block_device)
    return block_devices


def query_all_partitions(block_info: list[BlockInfo] | None = None) -> list[str]:
    """Query all partitions in block_info

    Args:
        block_info: list of block info queried. Optional

    Returns:
        list of partition paths
    """
    if block_info is None:
        block_info = query_all_block_info()
    partitions = []
    for block in block_info:
        for child in block.children:
            if child.is_partition():
                partitions.append(child.path)
    return partitions


def query_partition_info_by_path(path: str,
                                 block_info: list[BlockInfo] | None = None) -> BlockInfo | None:
    """Query block info for a partition.

    Args:
        path: Path to the partition.
        block_info: list of block info queried. Optional

    Returns:
        Block information or None if not found
    """
    if block_info is None:
        block_info = query_all_block_info()
    for block in block_info:
        for child in block.children:
            if child.is_partition() and child == path:
                return copy.deepcopy(child)
    return None


def query_partition_info_by_uuid(uuid: str,
                                 block_info: list[BlockInfo] | None = None) -> BlockInfo | None:
    """Query block info for partition with uuid

    Args:
        uuid: uuid of partition to query
        block_info: list of block info queried. Optional

    Returns:
        Block information or None if not found
    """
    if block_info is None:
        block_info = query_all_block_info()
    for block in block_info:
        for child in block.children:
            if child.is_partition() and child == uuid:
                return copy.deepcopy(child)
    return None


def query_partition_info_by_name(name: str,
                                 block_info: list[BlockInfo] | None = None) -> BlockInfo | None:
    """Query block info for partition with given name

    Args:
        name: Name of partition to query
        block_info: list of block info queried. Optional
    Returns:
        Block information or None if not found
    """
    if block_info is None:
        block_info = query_all_block_info()
    for block in block_info:
        for child in block.children:
            if child.is_partition() and child.name == name:
                return copy.deepcopy(child)
    return None

###############################################################################
# LVM support
###############################################################################


def lvm_scan_all() -> None:
    """Scans disks for LVM LVs
    """
    programs.Vgscan().invoke_and_wait(None, options={
        "q": None, "y": None})
    programs.Lvscan().invoke_and_wait(None, options={
        "q": None, "y": None})


def lvm_activate_all_vgs() -> None:
    """Activate all VGs
    """
    programs.Pvchange().invoke_and_wait(None, options={
        "q": None, "y": None, "a": "y"})

###############################################################################
# LUKS support
###############################################################################


def luks_is_partition_encrypted(path: str) -> bool:
    """Check if a partition is LUKS-encrypted

    Args:
        path: Path to partition to check

    Returns:
        Whatever the partition is LUKS-encrypted or not
    """
    errorcode = programs.Cryptsetup().invoke_and_wait(None, "isLuks", path)
    return not bool(errorcode)


def luks_open(path: str, name: str, passphrase: str) -> bool:
    """Open a LUKS-encrypted partition

    Args:
        path: Path to partition.
        name: Name of the produced device mapping.
        passphrase: passphrase to use for opening

    Returns:
        Whatever the operation was successful or not
    """
    cryptsetup = programs.Cryptsetup(
        stdout=programs.PIPE,
        stdin=programs.PIPE)
    cryptsetup.invoke("luksOpen", path, name)
    assert cryptsetup.stdin is not None
    cryptsetup.stdin.write(passphrase + "\n")
    cryptsetup.stdin.close()
    errorcode = cryptsetup.wait(None)
    return not bool(errorcode)


def luks_close(name: str) -> bool:
    """Close a LUKS-encrypted partition

    Args:
        name: name of the mapped device

    Returns:
        Whatever the operation was successful or not
    """
    errorcode = programs.Cryptsetup().invoke_and_wait(None, "luksClose", name)
    return not bool(errorcode)


###############################################################################
# Misc
###############################################################################


def get_partition_root(partition: str,
                       block_info: list[BlockInfo] | None = None) -> str | None:
    """Get the root block of a partition

    Args:
        partition: partition to look for.
        block_info: list of block info queried. Optional

    Returns:
        Path to the parent block or None if not found
    """
    if block_info is None:
        block_info = query_all_block_info()
    for block in block_info:
        if partition.startswith(block.path):
            return block.path
    # We cannot continue
    return None


def require_root_device(partition: str,
                        block_info: list[BlockInfo] | None = None) -> str:
    """Require root device of a partition

    Args:
        partition: Path to partition
        block_info: list of block info queried. Optional

    Raises:
        SystemExit: Finding the root device of the partition failed

    Returns:
        Root device of the partition
    """
    root_device = get_partition_root(partition, block_info)
    if root_device is None:
        raise SystemExit(1)
    return root_device


def setup(no_lvm: bool = False) -> tuple[list[BlockInfo], context.Context, str]:
    """Quick setup for storage.

    Handles LVM and returns all the block information

    Args:
        no_lvm: Don't discover LVM partitions

    Returns:
        a tuple of all block information, context for /, and the device the root partition resides on
    """
    if not no_lvm:
        lvm_scan_all()
        lvm_activate_all_vgs()
    block_info = query_all_block_info()
    return block_info, context.require_context_for_mount_point("/"), require_root_device("/")


def handle_luks_partition(part: str, passphrases: Iterable[str] = ()) -> tuple[str, str] | tuple[None, None]:
    """Handle a luks partition.

    First try all available passphrases, if none worked, try to get it interactively from the user.

    Args:
        part: Path to partition to mount
            passphrases: Passphrases to try if encountered an encrypted partition. Empty by default

    Returns:
        A tuple of where the partition is mounted and it's name.
        For example, for `/dev/sda3` it would be `("/dev/mapper/sda3_crypt", "sda3_crypt")`
        If failed, return a tuple of None (`(None, None)`)
    """
    luks_encrypted = luks_is_partition_encrypted(part)
    luks_name = part.split(os.path.sep)[-1] + "_crypt"
    if luks_encrypted:
        common_utils.print_info(
            "Luks encrypted partition found! Trying available passphrases...")
        for passphrase in passphrases:
            if luks_open(part, luks_name, passphrase):
                common_utils.print_info("Luks partition opened!")
                break
            try:
                common_utils.print_warning(
                    "Passphrase not found! Press Ctrl + C to try a passphrase")
                time.sleep(5)
            except KeyboardInterrupt:
                try:
                    while True:
                        common_utils.print_info(
                            "Enter new passphrase or press Ctrl + C again to abort: ", end="")
                        passphrase = input()
                        if luks_open(part, luks_name, passphrase):
                            common_utils.print_info(
                                "Luks partition opened!")
                            break
                except KeyboardInterrupt:
                    common_utils.print_warning(
                        f"No passphrase found for partition '{part}'")
                    return None, None
    part = f"/dev/mapper/{luks_name}"
    return luks_name, part


class MountedPartition(contextlib.AbstractContextManager['MountedPartition'], path_wrapper.PathWrapperBase, path_var_name="mount_point"):
    """A mounted partition

    Attributes:
        mount_point: Where the partition is mounted
    """
    _part: str
    _passphrases: Iterable[str]
    _no_luks: bool
    _is_luks_encrypted: bool
    _luks_name: str
    mount_point: str

    def __init__(self, part: str, passphrases: Iterable[str] = (), no_luks: bool = False):
        """Mount a partition

        Args:
            part: Path to partition to mount
            passphrases: Passphrases to try if encountered an encrypted partition. Empty by default
            no_luks: Do not attempt to unlock an encrypted partition. Defaults to False.
    """
        self._part = part
        self._passphrases = passphrases
        self._no_luks = no_luks
        super().__init__('/definitely-doesnt-exist-and-also-shouldnt')

    def __enter__(self) -> 'MountedPartition':
        if not self._no_luks:
            is_luks_encrypted = luks_is_partition_encrypted(self._part)

            if is_luks_encrypted:
                tmp, tmp2 = handle_luks_partition(
                    self._part, self._passphrases)
                if tmp is None or tmp2 is None:
                    raise RuntimeError(
                        f"Failed to unlock partition '{self._part}'")
                luks_name, part = tmp, tmp2
        else:
            is_luks_encrypted = False
        mount_point = tempfile.mkdtemp()
        errorcode = programs.Mount().invoke_and_wait(None, part, mount_point)
        if errorcode != 0:
            common_utils.print_error(
                f"Failed to mount partition '{part}'! Skipping partition")
            if is_luks_encrypted:
                luks_close(luks_name)
            raise RuntimeError(
                f"Failed to mount partition '{part}'! Skipping partition")

        self._luks_name = luks_name
        self._is_luks_encrypted = is_luks_encrypted
        self.mount_point = mount_point
        return self

    def __exit__(self, *_: Any) -> None: 
        programs.Umount().invoke_and_wait(None, self.mount_point)
        if hasattr(self, "is_luks_encrypted"):
            luks_close(self._luks_name)


def mount_partition(part: str, passphrases: Iterable[str] = (), no_luks: bool = False) -> MountedPartition:
    """Mount a partition

    Args:
        part: Path to partition to mount
        passphrases: Passphrases to try if encountered an encrypted partition. Empty by default
        no_luks: Do not attempt to unlock an encrypted partition. Defaults to False.

    Returns:
        mounted partition
    """
    return MountedPartition(part, passphrases, no_luks)
