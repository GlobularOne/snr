"""
Access and copy files by pattern
"""

from snr.core.payload.payload import REQUIRED, Context, Payload


class FilesPayload(Payload):
    AUTHORS = ("GlobularOne",)
    TARGET_OS_LIST = ("Microsoft Windows", "GNU/Linux")
    INPUTS = (
        ("PATTERNS", [], -1, "Glob pattern for files to copy", REQUIRED),
        Payload.supports_encrypted_access()
    )

    def generate(self, ctx: Context) -> int:
        variables = self.get_self_variables()
        self.format_payload_and_write(ctx, variables)
        self.add_autorun(ctx)
        return 0


payload = FilesPayload()
