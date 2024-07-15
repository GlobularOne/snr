"""
Other commands
"""
import pdb
import sys
from typing import NoReturn

import click
import rich.table

from snr.cli import atexit_callbacks, interactive_shell, variables
from snr.core.core import console, options
from snr.core.util import common_utils, programs


@interactive_shell.interactive_shell.command("clear")
def cmd_clear() -> None:
    """\
Clear the screen
    """
    common_utils.clear_screen()


@interactive_shell.interactive_shell.command("echo")
@click.argument("value", nargs=-1, required=False)
def cmd_echo(value: tuple[str, ...] | None) -> str | None:
    """\
Echo the arguments
    """
    return " ".join(value) if value is not None else ""


@interactive_shell.interactive_shell.command("exit")
@click.argument("value", nargs=-1, required=False)
def cmd_exit(value: tuple[str, ...] | None) -> NoReturn:
    """\
Exit the interactive environment
    """
    if value is not None:
        print(" ".join(value), file=sys.stderr)
    sys.exit(options.default_exit_code)


@interactive_shell.interactive_shell.command(name="help")
@click.argument("value", required=False)
def cmd_help(value: str | None) -> str | None:
    """\
Print help on a specific command or variable, or list all commands
    """
    if value is None:
        table = rich.table.Table(title="Commands")
        table.add_column("Command", style="blue")
        table.add_column("Help", style="red")
        for command, func in interactive_shell.interactive_shell.commands.items():
            table.add_row(command,
                          getattr(func,
                                  "__doc__",
                                  "Not documented").replace("\n", " "))
        console.console.print(table)
        return None
    if value == "payload":
        if options.payload_module is None:
            common_utils.print_error("No payload selected")
            return None
        doc = getattr(options.payload_module,
                      "__doc__",
                      "Not documented")
        inputs = getattr(getattr(options.payload_module, "payload"),
                         "INPUTS",
                         (("No inputs specified",),))
        authors = getattr(getattr(options.payload_module, "payload"),
                          "AUTHORS",
                          ["No authors specified"])
        license_info = getattr(getattr(options.payload_module, "payload"),
                               "LICENSE",
                               "gpl-3.0")
        dependencies = getattr(getattr(options.payload_module, "payload"),
                               "DEPENDENCIES")
        target_os_list = getattr(getattr(options.payload_module, "payload"),
                                 "TARGET_OS_LIST", ("None specified"))
        return f"""\
Payload path: [blue]{options.payload_path}[/blue]
Input: [blue]{' '.join([inp[0] for inp in inputs])}[/blue]
Authors: [blue]{' '.join(authors)}[/blue]
License: [blue]{license_info}[/blue]
Dependencies: [blue]{' '.join(dependencies)}[/blue]
Supported Operating Systems: [blue]{' '.join(target_os_list)}[/blue]
[blue]{doc}[/blue]"""
    if value in interactive_shell.interactive_shell.commands:
        return getattr(
            interactive_shell.interactive_shell.commands.get(value),
            "__doc__",
            "Not documented")
    if variables.global_vars.has_variable(value):
        info = variables.global_vars.get_variable_info(value)
        doc = info.description if info.description != "" else "Not documented"
        return doc
    return None


@interactive_shell.interactive_shell.command(name="info")
@click.pass_context
def cmd_info(ctx: click.Context) -> str:
    """\
Print information on the loaded payload. Same as `help payload`
    """
    return interactive_shell.dispatch_command(
        ctx, interactive_shell.interactive_shell, "help payload")


@interactive_shell.interactive_shell.command(name="pdb")
def cmd_pdb() -> None:
    """\
Drop to a debugging shell. For debugging purposes only
"""
    pdb.set_trace()  # pylint: disable=no-member


@interactive_shell.interactive_shell.command(name="reload")
def cmd_reload() -> str | None:
    """\
Reload the shell
    """
    common_utils.print_warning(
        "Reloading shell, shell state will not be saved!")
    atexit_callbacks.restore_cwd()
    # The reloaded shell will do those anyway
    atexit_callbacks.unregister_atexit_callbacks()
    common_utils.print_debug(f"Executing '{' '.join(sys.orig_argv)}'")
    Python = programs.program_wrapper_factory(sys.orig_argv[0])
    errorcode = Python().invoke_and_wait(None, *sys.orig_argv[1:])
    raise SystemExit(errorcode)
