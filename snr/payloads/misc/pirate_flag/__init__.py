"""
Show a pirate flag with a red background. Not very practical, included only for pranking
"""
from snr.core.payload.payload import Payload, Context


class PirateFlagPayload(Payload):
    AUTHORS = ("GlobularOne",)

    def generate(self, ctx: Context) -> int:
        self.copy_root_to_root(
            ctx, __file__, "payload.py", "root/payload.py")
        self.add_autorun(ctx, "root/payload.py")
        return 0


payload = PirateFlagPayload()
