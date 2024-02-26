"""
Other commands
"""
import os as _os
import sys as _sys

from libsnr.core import options as _options
from libsnr.util.common_utils import clear_screen as _clear_screen
from libsnr.util.common_utils import print_debug as _print_debug
from libsnr.util.common_utils import print_error as _print_error
from libsnr.util.common_utils import print_warning as _print_warning
from libsnr.util.table import Table as _Table

from snr import atexit_callbacks as _atexist_callbacks
from snr import command_utils as _command_utils
from snr.variables import global_vars as _global_vars


def cmd_clear(_, __):
    """\
Clear the screen
    """
    _clear_screen()


def cmd_echo(argv: list[str], _):
    """\
Echo the arguments
    """
    return " ".join(argv)


def cmd_exit(argv: list[str], argc: int):
    """\
Exit the interactive environment
    """
    if not _options.interactive:
        _print_debug("Exit command called while not in interactive mode")
    if argc != 0:
        print(*argv, file=_sys.stderr)
    _sys.exit(_options.default_exit_code)


def cmd_help(argv: list[str], argc: int):
    """\
Print help on a specific command or variable, or list all commands
    """
    if argc == 0:
        table = _Table("Commands")
        for command, func in _command_utils.commands.items():
            table.add_row(command,
                          getattr(func,
                                  "__doc__",
                                  "Not documented").replace("\n", " "))
        return str(table)
    args = " ".join(argv)
    if args == "payload":
        if _options.payload_module is None:
            return "No payload selected"
        doc = getattr(_options.payload_module,
                      "__doc__",
                      "Not documented")
        inputs = getattr(_options.payload_module,
                         "INPUTS",
                         ["No inputs specified"])
        authors = getattr(_options.payload_module,
                          "AUTHORS",
                          ["No authors specified"])
        license_info = getattr(_options.payload_module,
                          "LICENSE",
                          "Apache-2.0")
        dependencies = getattr(_options.payload_module,
                               "DEPENDENCIES",
                               ["No dependencies specified"])
        return f"""\
Payload path: {_options.payload_path}
Input: {' '.join(inputs)}
Authors: {' '.join(authors)}
license: {license_info}
dependencies: {' '.join(dependencies)}
{doc}
"""
    if args in _command_utils.commands:
        return getattr(
            _command_utils.commands[args],
            "__doc__",
            "Not documented")
    if _global_vars.has_variable(args):
        info = _global_vars.get_variable_info(args)
        doc = info.description if info.description != "" else "Not documented"
        return doc
    return None


def cmd_info(_, __):
    """\
Print information on the loaded payload. Same as `help payload`
    """
    cmd_help(["payload"], 1)


def cmd_reload(_, __):
    """\
Reload the shell
    """
    if not _options.interactive:
        return _print_error("Cannot reload in interactive mode")
    _print_warning("Reloading shell, shell state will not be saved!")
    _atexist_callbacks.restore_cwd()
    # The reloaded shell will do those anyway
    _atexist_callbacks.unregister_atexit_callbacks()
    errorcode = _os.system(" ".join(_sys.orig_argv))
    raise SystemExit(errorcode)
