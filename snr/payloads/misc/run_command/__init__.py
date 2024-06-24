"""
Run a command or executable on boot, the executable must exist on the host filesystem.
If you want to run an executable that is locally available. Use run_executable.
It finds the executable and copies it onto the host filesystem.
"""
from snr.core.payload.payload import Payload, Context
from snr.core.util import common_utils
from snr.cli import variables as cli_variables

class RunCommandPayload(Payload):
    AUTHORS = ("GlobularOne",)

    INPUTS = (
        ("COMMANDS", [], -1, "Command to run"),
    )

    def generate(self, ctx: Context) -> int:
        variables = self.get_self_variables()
        assert isinstance(variables["COMMANDS"], list)
        if cli_variables.global_vars.has_variable("COMMAND"):
            common_utils.print_warning("COMMAND is depreciated and will soon be removed, use COMMANDS")
            assert isinstance(variables["COMMAND"], str)
            variables["COMMANDS"].append(variables["COMMAND"])
        if len(variables["COMMANDS"]) == 0:
            common_utils.print_error("Nothing selected to run")
            return 1
        with common_utils.rootfs_open(ctx, "root/payload.sh", "w", encoding="utf-8") as stream:
            stream.write("#!/bin/bash\n")
            for command in variables["COMMANDS"]:
                stream.write(command)
                stream.write("\n")
        self.add_autorun(ctx, "root/payload.sh")
        return 0


payload = RunCommandPayload()
