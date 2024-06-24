"""
Drop to a shell as root
"""

from snr.core.payload.payload import Payload, Context


class ShellPayload(Payload):
    AUTHORS = ("GlobularOne",)

    def generate(self, _: Context) -> int:
        # Do nothing, really nothing
        return 0


payload = ShellPayload()
