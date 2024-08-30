#!/usr/bin/python3
"""
Files payload
"""
import glob

from snr.core.payload import data_dir, entry_point, storage
from snr.core.util import common_utils

PATTERNS = "@PATTERNS@"
PASSPHRASES = "@PASSPHRASES@"


@entry_point.entry_point
def main(block_info: storage.BlocksType, *_) -> None:
    for part in storage.query_all_partitions(block_info):
        with storage.mount_partition(part, PASSPHRASES) as mounted_part:
            part_info = storage.query_partition_info_by_path(part, block_info)
            assert part_info is not None
            part_data = data_dir.wrap_data_path_for_block(part_info)
            for pattern in PATTERNS:
                paths = glob.glob(pattern, root_dir=mounted_part.mount_point,
                                  recursive=True)
                common_utils.print_info(
                    f"Pattern '{pattern}' resulted into {len(paths)} matches. Copying...")
                for path in paths:
                    src_path = mounted_part.join(path)
                    # Remake the structure
                    # If the matched path is a directory, just pass it to makedirs
                    # If it is a file, create it's parents, and then copy the file
                    if part_data.isdir(path):
                        part_data.makedirs(path)
                        # Copy the whole tree
                        part_data.copytree(
                            src_path, path, ignore_dangling_symlinks=True, dirs_exist_ok=True)
                    else:
                        part_data.makedirs(part_data.dirname(path))
                        part_data.copy(src_path, path)

if __name__ == "__main__":
    main()
