"""
Core code of the interactive shell
"""
import bdb
import shlex
import pathlib
import os
import os.path
from typing import Any

import click
import prompt_toolkit
import prompt_toolkit.auto_suggest
import prompt_toolkit.history
import prompt_toolkit.lexers
import prompt_toolkit.styles
import pygments.styles
import pyfiglet

from snr import version
from snr.cli import lexer, variables
from snr.core.core import common_paths, console, options
from snr.core.util import common_utils


__all__ = (
    "prompt", "dispatch_command",
    "handle_non_interactive_mode", "interactive_shell"
)

prompt: str


def _count_payloads() -> int:
    try:
        count = 0
        payload_set_dir = os.path.join(
            common_paths.PAYLOAD_SET_PATH)
        categories = os.listdir(payload_set_dir)
        for category in categories:
            category_path = os.path.join(payload_set_dir, category)
            if os.path.isdir(category_path):
                for content in os.listdir(category_path):
                    payload_path = os.path.join(category_path, content)
                    if os.path.isdir(payload_path) and os.path.exists(os.path.join(payload_path, "__init__.py")):
                        count += 1
        return count

    except Exception as exc:  # pylint: disable=broad-exception-caught
        common_utils.print_info(f"Failed to count payloads: {exc}")
        return 0


def _format_banner() -> str:
    banner = pyfiglet.Figlet(font="slant").renderText("stick->'n'->run")
    return f"[blue]{banner}[/blue]\n" + \
        f"--> Version: [red]{version.__version__}[/red]\n" + \
        f"--> Homepage: [red]{version.HOMEPAGE}[/red]\n" + \
        f"--> [red]{_count_payloads()}[/red] Available Payloads\n"


def _expand_vars(line: list[str]) -> list[str]:
    new_cmdline: list[str] = []
    for arg in line:
        if arg.startswith("$") and not arg.startswith("\\$"):
            # This argument must be replaced
            var_name = arg.removeprefix("$")
            if variables.global_vars.has_variable(var_name):
                # Format it, it is either str, int, bool or a list of those
                var_value = variables.global_vars.get_variable(var_name)
                if isinstance(var_value, (int, bool)):
                    var_value = str(var_value)
                elif isinstance(var_value, list):
                    var_value = ";".join(*map(str, var_value))
                new_cmdline.append(var_value)
            else:
                common_utils.print_error(f"No variable named '{var_name}'")
                new_cmdline.append(arg)
        else:
            new_cmdline.append(arg)
    return new_cmdline


def _read_input(session: prompt_toolkit.PromptSession[str]) -> str:

    return session.prompt([("class:prompt", prompt)])


def dispatch_command(ctx: click.Context, group: click.Group, line: str) -> str:
    """Dispatch a command

    Args:
        ctx: Click context
        group: Group to dispatch command
        line: Command and it's arguments

    Returns:
        Return value of command, or an empty string if it didn't return anything
    """
    if len(line) == 0:
        return ""
    command = line.split()[0]
    args = line.split()[1:]
    args = _expand_vars(args)
    subcommand = group.commands.get(command)
    if subcommand:
        ctx.params.clear()
        try:
            subcommand.parse_args(ctx, args)
            output: str | None = ctx.forward(subcommand)
            if output is None:
                return ""
            return output
        except bdb.BdbQuit:
            pass
        except common_utils.UserError as exc:
            common_utils.print_error(exc.message)
        except click.UsageError as e:
            console.console.print(e.format_message())
        except Exception:  # pylint: disable=broad-exception-caught
            common_utils.print_error(
                "Executing a command failed."
                " This is likely to be an issue in snr itself."
                f" Please report this issue at {version.HOMEPAGE}/issues")
            common_utils.handle_exception()
        finally:
            # Do not forget to clear the parsed args, otherwise parsed data will transfer to the next command
            ctx.params.clear()
    else:
        common_utils.print_sys(f"No command named '{command}' found")
    return ""


def handle_non_interactive_mode(ctx: click.Context, **kwargs: Any) -> None:
    """Handle non-interactive mode of shell

    Args:
        ctx: Click context
    """
    assert isinstance(kwargs["payload"], str)
    assert isinstance(kwargs["defines"], tuple)
    assert isinstance(kwargs["output"], str)
    payload: str = kwargs["payload"]
    defines: tuple[str, ...] = kwargs["defines"]
    output: str = kwargs["output"]
    payload_abs = os.path.join(os.getcwd(), payload)
    if not pathlib.Path(payload_abs).resolve().is_relative_to(os.getcwd()):
        # Not today for path traversal
        common_utils.print_fatal("Payload is not a builtin payload")
    if shlex.quote(payload) != payload:
        common_utils.print_fatal("Invalid payload name")
    common_utils.print_debug("Starting generation of command list")
    commands = [
        f"use {pathlib.Path(payload_abs).resolve().relative_to(os.getcwd())}"
    ]
    # Now handle variables
    for define in defines:
        name, value = define.split("=", maxsplit=1)
        if name.startswith("!") or shlex.quote(name) != name:
            common_utils.print_fatal(f"Invalid define name: {name}")
        common_utils.print_debug(f"Defining variable {name}")
        commands.append(f"set {name} {value}")
    common_utils.print_debug("Adding generate command")
    commands.append(f"generate {output}")
    common_utils.print_debug("Command list:\n", commands)
    for command in commands:
        common_utils.print_debug(f"Executing command: {command}")
        dispatch_command(ctx, interactive_shell, command)


@click.group(name="interactive_shell",
             invoke_without_command=True)
@click.pass_context
@click.option("--verbose", "-v", is_flag=True)
@click.option("--quiet", "-q", is_flag=True)
@click.option("--arch", "payload_arch")
@click.option("--init", "do_init", is_flag=True)
@click.option("--init-only", is_flag=True)
@click.option("--init-if-needed", is_flag=True)
@click.option("--reinit", "do_reinit", is_flag=True)
@click.option("--host-primary-nameserver")
@click.option("--host-secondary-nameserver")
@click.option("--host-hostname")
@click.option("--user-agent")
@click.option("--default-exit-code")
@click.option("--debug", is_flag=True)
@click.option("--version", is_flag=True)
def interactive_shell(ctx: click.Context, /, **kwargs: dict[str, Any]) -> None:
    """Interactive shell's main function

    Args:
        ctx: Click context
    """
    global prompt  # pylint: disable=global-statement
    if ctx.invoked_subcommand is None:
        # Do not pass the program's params to the shell commands
        ctx.params.clear()
        prompt = options.PROMPT_UNLOADED
        if not options.quiet:
            console.console.print(_format_banner())
        common_utils.print_debug(
            "Command line loop reached. Initialization finished")
        session: prompt_toolkit.PromptSession[str] = prompt_toolkit.PromptSession(
            history=prompt_toolkit.history.FileHistory(
                os.path.join(common_paths.STATE_PATH, "history.txt")),
            auto_suggest=prompt_toolkit.auto_suggest.AutoSuggestFromHistory(),
            lexer=prompt_toolkit.lexers.PygmentsLexer(
                lexer.SnrLexer) if not options.quiet else None,
            style=prompt_toolkit.styles.merge_styles([
                prompt_toolkit.styles.style_from_pygments_cls(
                    pygments.styles.get_style_by_name("vs")),
                prompt_toolkit.styles.Style.from_dict({
                    "prompt": "#00e000 bold",
                })
            ]))
        if "payload" in kwargs:
            handle_non_interactive_mode(ctx, **kwargs)
            return
        while True:
            console.console.print(dispatch_command(
                ctx, interactive_shell, _read_input(session)))
