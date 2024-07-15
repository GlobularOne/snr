"""
Run an executable on boot, the executable will be copied to the host filesystem.
If you want to run an executable that is already available on the host. Use run_command.
It does not copy the executable onto the host filesystem.
Do note that this payload does preserve ordering
"""
import os.path
import shutil

from snr.core.payload.payload import Context, Payload
from snr.core.util import common_utils


class RunCommandPayload(Payload):
    AUTHORS = ("GlobularOne",)
    TARGET_OS_LIST = ("Any",)
    INPUTS = (
        ("EXECUTABLES", [], -1, "Executables to copy and run", True),
    )

    def generate(self, ctx: Context) -> int:
        variables = self.get_self_variables()
        assert isinstance(variables["EXECUTABLES"], list)
        if len(variables["EXECUTABLES"]) == 0:
            common_utils.print_error("Nothing selected to run")
            return 1
        for executable in variables["EXECUTABLES"]:
            basename = os.path.basename(executable)
            target = os.path.join("root", basename)
            if not os.path.isabs(executable):
                # Does it exist on the current working directory?
                if os.path.exists(os.path.abspath(executable)):
                    # Then it's fine
                    executable = os.path.abspath(executable)
                else:
                    # Does it exist on PATH?
                    tmp = shutil.which(executable)
                    if tmp is None:
                        # We can't find it
                        common_utils.print_error(
                            f"Could not find '{executable}'! Check that you have typed correctly")
                        return 1
                    else:
                        executable = tmp

            common_utils.print_debug(f"Copying '{executable}' to '{target}'")
            try:
                shutil.copyfile(executable, ctx.join(target))
            except (OSError, shutil.Error) as exc:
                common_utils.print_error(
                    f"Installing executable to rootfs failed: {exc}")
                return 1
            common_utils.print_debug(
                f"Adding autorun service for '{executable}'")
            self.add_autorun(ctx, os.path.join("/", target))
        return 0


payload = RunCommandPayload()
