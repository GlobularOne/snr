"""
Run a command or executable on boot, the executable must exist on the host filesystem.
If you want to run an executable that is locally available. Use run_executable.
It finds the executable and copies it onto the host filesystem.
"""
from snr.core.payload.payload import REQUIRED, VALID_STRING, Context, Payload
from snr.core.util import common_utils


class RunCommandPayload(Payload):
    AUTHORS = ("GlobularOne",)
    TARGET_OS_LIST = ("Any",)
    INPUTS = (
        ("COMMANDS", [], -1, "Command to run", REQUIRED | VALID_STRING),
    )

    def generate(self, ctx: Context) -> int:
        variables = self.get_self_variables()
        assert isinstance(variables["COMMANDS"], list)
        with ctx.open("root/payload.sh", "w", encoding="utf-8") as stream:
            stream.write("#!/bin/bash\n")
            for command in variables["COMMANDS"]:
                stream.write(command)
                stream.write("\n")
        self.add_autorun(ctx, "root/payload.sh")
        return 0


payload = RunCommandPayload()
