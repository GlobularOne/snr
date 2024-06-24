#!/usr/bin/python3
"""
"""
import random

from snr.core.payload import context, entry_point, storage
from snr.core.util import common_utils

WIPE_MODE = "@WIPE_MODE@"


def pass_zero(path: str, kbs: int) -> None:
    with open(path, "wb") as stream:
        for _ in range(kbs):
            stream.write(b'\0' * 1024)
            stream.flush()


def pass_ff(path: str, kbs: int) -> None:
    with open(path, "wb") as stream:
        for _ in range(kbs):
            stream.write(b'\xFF' * 1024)
            stream.flush()


def pass_random(path: str, kbs: int) -> None:
    with open(path, "wb") as stream:
        for _ in range(kbs):
            stream.write(random.randbytes(1024))
            stream.flush()


@entry_point.entry_point
def main() -> None:
    storage.lvm_scan_all()
    storage.lvm_activate_all_vgs()
    block_info = storage.query_all_block_info()
    wipe_level = ord(WIPE_MODE) - ord("A")
    common_utils.print_ok("Wipe_disks payload started")
    # We need a context for our root, to not wipe ourselves
    ctx = context.create_context_for_mount_point("/")
    if ctx is None:
        common_utils.print_error("Creating context for / failed")
        # We cannot continue
        return None
    our_device = storage.get_partition_root(ctx.device_name, block_info)
    if our_device is None:
        common_utils.print_error("Finding partition root device for / failed")
        return None
    for block in block_info:
        if block != our_device and not block.is_rom():
            common_utils.print_info(f"Targeting {block.path}")
            # Level 0: All levels have this
            # No matter the mode, we must override the partition table header and filesystem header
            for child in block.children:
                common_utils.print_info(
                    f"Wiping filesystem info on {child.path}")
                pass_zero(child.path, 1024)
            common_utils.print_info(f"Wiping partition table on {block.path}")
            pass_zero(block.path, 1024)
            if wipe_level >= 1:
                common_utils.print_info(f"Doing a zero pass on {block.path}")
                pass_zero(block.path, block.size // 1024)
            if wipe_level >= 2:
                common_utils.print_info(f"Doing a 0xFF pass on {block.path}")
                pass_ff(block.path, block.size // 1024)
            if wipe_level >= 3:
                common_utils.print_info(f"Doing a random pass on {block.path}")
                pass_random(block.path, block.size // 1024)
            if wipe_level >= 4:
                for _ in range(5-1):
                    common_utils.print_info(
                        f"Doing a random pass on {block.path}")
                    pass_random(block.path, block.size // 1024)
    common_utils.print_ok("Wipe_disks payload completed")
    return None


if __name__ == "__main__":
    main()
