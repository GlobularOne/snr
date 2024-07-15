"""
Drop to a shell as root
"""

from snr.core.payload.payload import Context, Payload


class ShellPayload(Payload):
    AUTHORS = ("GlobularOne",)
    TARGET_OS_LIST = ("Any",)

    def generate(self, _: Context) -> int:
        # Do nothing, really nothing
        return 0


payload = ShellPayload()
