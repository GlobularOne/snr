"""
Create a SSH server
"""

from snr.core.payload.payload import Context, Payload


class SSHServerPayload(Payload):
    AUTHORS = ("GlobularOne",)
    TARGET_OS_LIST = ("Any",)
    INPUTS = (
        ("PUBLIC_KEY", "", -1, "Public key for key-based authentication", True),
    )
    DEPENDENCIES = (
        "openssh-server",
    )

    def generate(self, ctx: Context) -> int:
        variables = self.get_self_variables()
        ctx.makedirs("root/.ssh")
        with ctx.open("root/.ssh/authorized_keys", "w") as stream:
            stream.write(variables["PUBLIC_KEY"])
        return 0


payload = SSHServerPayload()
