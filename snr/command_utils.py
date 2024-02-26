"""
Module containing utilities to dispatch commands and implements them
"""
import traceback as _traceback

from libsnr.util.common_utils import print_error as _print_error
from libsnr.util.common_utils import print_sys as _print_sys
from libsnr.version import HOMEPAGE as _HOMEPAGE

from snr.variables import global_vars as _global_vars

commands = {}


def dispatch_command(cmdline: str) -> str | None:
    """
    Dispatch a command from given string
    """
    if len(cmdline) == 0:
        return None
    orig_argv = cmdline.split()
    new_cmdline = ""
    argc = len(orig_argv)
    # First process variables
    for arg in orig_argv:
        if arg.startswith("$") and not arg.startswith("\\$"):
            # This argument must be replaced
            var_name = arg.removeprefix("$")
            if _global_vars.has_variable(var_name):
                # Format it, it is either str, int, bool or a list of those
                var_value = _global_vars.get_variable(var_name)
                if isinstance(var_value, (int, bool)):
                    var_value = str(var_value)
                elif isinstance(var_value, list):
                    var_value = ";".join(*map(str, var_value))
                new_cmdline += var_value + " "
            else:
                _print_error(f"No variable named '{var_name}'")
                return None
        else:
            new_cmdline += arg + " "
    argv = new_cmdline.split()
    argc = len(argv)
    if argv[0] in commands:
        try:
            return commands[argv[0]](argv[1:], argc-1)
        except Exception:  # pylint: disable=broad-exception-caught
            _print_error(
                "Executing a command failed."
                " This is likely to be an issue in snr itself."
                f" Please report this issue at {_HOMEPAGE}/issues")
            print(">>>>>> START OF TRACEBACK <<<<<<")
            _traceback.print_stack()
            _traceback.print_exc()
            print(">>>>>> END OF TRACEBACK <<<<<<")
    else:
        _print_sys(f"Command '{argv[0]}' not found")
    return None
