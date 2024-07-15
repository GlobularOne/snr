"""
Extract all account login hashes
"""

from snr.core.payload.payload import Context, Payload


class AccountHashesPayload(Payload):
    AUTHORS = ("GlobularOne",)
    TARGET_OS_LIST = ("Microsoft Windows", "GNU/Linux")
    ROOTFS_VERSION = 2
    INPUTS = (
        ("PASSPHRASES", [], -1, "Passphrases to try for LUKS-encrypted partitions"),
    )

    def generate(self, ctx: Context) -> int:
        variables = self.get_self_variables()
        self.format_payload_and_write(ctx, variables)
        self.add_autorun(ctx)
        return 0


payload = AccountHashesPayload()
