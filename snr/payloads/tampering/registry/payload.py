#!/usr/bin/python3
"""
Registry payload
"""
from snr.core.payload import (entry_point, storage, nt_registry)
from snr.core.util import common_utils

REGISTRIES = "@REGISTRIES@"
PASSPHRASES = "@PASSPHRASES@"


@entry_point.entry_point
def main() -> None:
    block_info, _, our_device = storage.setup()
    common_utils.print_info("Registry payload started")
    for part in storage.query_all_partitions(block_info):
        if storage.get_partition_root(part, block_info) == our_device:
            continue
        with storage.mount_partition(part, PASSPHRASES) as mounted_part:
            if mounted_part.exists("Windows"):
                with nt_registry.NtRegistry(mounted_part) as reg:
                    for raw_key in REGISTRIES:
                        name, key, type_ = raw_key.split(":", maxsplit=2)
                        node = reg.find_node(name)
                        if node is None:
                            # Create it
                            hive_path = "\\".join(name.split("\\")[:2])
                            parent_node = reg.find_node(hive_path)
                            assert parent_node is not None
                            for node_path in name.split("\\")[2:]:
                                new_node = parent_node.find_child(node_path)
                                if new_node is None:
                                    new_node = parent_node.new_child(node_path)
                                parent_node = new_node
                            # Now parent_node is our node
                            node = parent_node
                        node.new_data(key, getattr(
                            nt_registry, type_), REGISTRIES[raw_key])
            else:
                common_utils.print_warning("Unknown operating system!")
    common_utils.print_ok("Registry payload completed")
