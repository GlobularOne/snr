#!/usr/bin/python3
"""
Files payload
"""
import glob
import os

from snr.core.payload import entry_point, storage
from snr.core.util import common_utils

FILES = "@FILES@"
PASSPHRASES = "@PASSPHRASES@"


@entry_point.entry_point
def main() -> None:
    block_info, _, our_device = storage.setup()
    common_utils.print_info("Files payload started")
    for part in storage.query_all_partitions(block_info):
        if storage.get_partition_root(part, block_info) == our_device:
            continue
        with storage.mount_partition(part, PASSPHRASES) as mounted_part:
            for file in FILES:
                pattern, action, arg = file.split(":", maxsplit=2)
                paths = glob.glob(pattern, root_dir=mounted_part.mount_point,
                                  recursive=True)
                common_utils.print_info(
                    f"Pattern '{pattern}' resulted into {len(paths)} matches. Modifying...")
                for path in paths:
                    if mounted_part.isdir(path):
                        mounted_part.rmtree(path)
                    else:
                        mounted_part.remove(path)
                    match action:
                        case "delete":
                            # Already done
                            pass
                        case "replace":
                            try:
                                if mounted_part.isdir(arg):
                                    mounted_part.copytree(
                                        os.path.join(os.getcwd(), arg), path)
                                else:
                                    mounted_part.copy(arg, path)
                            except Exception:
                                common_utils.print_warning(
                                    f"Replace action failed on {mounted_part.join(path)}")
                        case "replace_local":
                            try:
                                if mounted_part.isdir(arg):
                                    mounted_part.copytree(arg, path)
                                else:
                                    mounted_part.copy(arg, path)
                            except Exception:
                                common_utils.print_warning(
                                    f"Replace_local action failed on {mounted_part.join(path)}")
    common_utils.print_ok("Files payload completed")
