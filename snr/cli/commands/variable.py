"""
Variable-related commands
"""

import click
import rich.console
import rich.pretty
import rich.table

from snr.cli import interactive_shell, variables
from snr.core.core import variable_manager
from snr.core.util import common_utils

NORMAL_TYPES = {
    "str": "String",
    "int": "Number",
    "bool": "Option",
    "list": "String List"
}

REQUIRED_STATES = {
    True: "Required",
    False: "Not required"
}

DESCRIPTIVE_TYPES = {
    "String": {
        variable_manager.VariableFlags.VALID_STR_ALPHA: "Alphabetic String",
        variable_manager.VariableFlags.VALID_STR_ALPHANUM: "Alphabetic-number String",
        variable_manager.VariableFlags.VALID_STR_ASCII: "ASCII-only String",
        variable_manager.VariableFlags.VALID_STR_PATH_COMPONENT: "Path Component",
        variable_manager.VariableFlags.VALID_STR_HOST_PATH: "Host Path",
        variable_manager.VariableFlags.VALID_STR_LOCAL_PATH: "Local Path",
        variable_manager.VALID_IP: "IP Address",
        variable_manager.VALID_IPV4: "IPv4 Address",
        variable_manager.VALID_IPV6: "IPv6 Address",
    },
    "Number": {
        variable_manager.VALID_IP: "Port Number"
    },
    "String List": {
        variable_manager.VariableFlags.VALID_STR_ALPHA: "List of Alphabetic Strings",
        variable_manager.VariableFlags.VALID_STR_ALPHANUM: "List of Alphabetic-number Strings",
        variable_manager.VariableFlags.VALID_STR_ASCII: "List of ASCII-only Strings",
        variable_manager.VariableFlags.VALID_STR_PATH_COMPONENT: "List of Path Components",
        variable_manager.VariableFlags.VALID_STR_HOST_PATH: "List of Host Paths",
        variable_manager.VariableFlags.VALID_STR_LOCAL_PATH: "List of Local Paths",
        variable_manager.VALID_IP: "List of IP Addresses",
        variable_manager.VALID_IPV4: "List of IPv4 Addresses",
        variable_manager.VALID_IPV6: "List of IPv6 Addresses",
    }
}


@interactive_shell.interactive_shell.command(name="unset")
@click.argument("name", required=True)
def cmd_unset(name: str) -> str | None:
    """\
Unset a variable
    """
    if not variables.global_vars.has_variable(name):
        common_utils.print_error(f"No variable named '{name}'")
        return None
    if variables.global_vars.get_variable_info(name).flags & variable_manager.USED_BY_PAYLOAD:
        variables.global_vars.set_variable(
            name, variables.global_vars.get_variable_info(name).default_value)
        common_utils.print_info(
            f"[blue]{name}[/blue][green] =>[/green]",
            rich.pretty.Pretty(variables.global_vars.get_variable_info(name).default_value))
    else:
        variables.global_vars.del_variable(name)
    return None


@interactive_shell.interactive_shell.command(name="set")
@click.argument("name", required=False)
@click.argument("value", nargs=-1, required=False)
@click.pass_context
def cmd_set(ctx: click.Context, name: str | None, value: tuple[str, ...] | None) -> str | None:  # pylint: disable=too-many-return-statements
    """\
Set value of a variable (syntax: set <variable name> <value>).
Or unset a variable (syntax: set <variable name>).
Or list all variables (syntax: set)
    """
    if name is None:
        table = rich.table.Table(title="Variables")
        table.add_column("Name", style="blue")
        table.add_column("Type", style="red")
        table.add_column("Required", style="cyan")
        table.add_column("Length Limit", style="magenta")
        table.add_column("Value")
        table.add_column("Description", style="green")
        for var_name, info in zip(variables.global_vars.get_variables_name(),
                                  variables.global_vars.get_variables_info()):
            var_type = NORMAL_TYPES[str(info.var_type.__name__)]
            if var_type in DESCRIPTIVE_TYPES:
                for flag in info.flags:
                    if flag in DESCRIPTIVE_TYPES[var_type]:
                        var_type = DESCRIPTIVE_TYPES[var_type][flag]
            var_len = str(info.length) if info.length != -1 else "Unlimited"
            var_value = variables.global_vars.get_variable(var_name)
            if isinstance(var_value, list):
                var_value = " ".join(map(str, var_value))
            else:
                var_value = str(var_value)
            table.add_row(var_name, var_type, REQUIRED_STATES[bool(info.flags & variable_manager.REQUIRED)], var_len,
                          var_value, info.description)
        if table.row_count == 0:
            table.add_row("", "", "", "", "")
        rich.console.Console().print(table)
        return None
    if value is None or len(value) == 0:
        return interactive_shell.dispatch_command(ctx, interactive_shell.interactive_shell, f"unset {name}")
    # Two scenarios are possible:
    #   1. The variable already exists, so already has type information
    #   2. The variable doesn't exist, so type is str
    assert value is not None
    if name.startswith("!"):
        # The value is a command to execute
        name = name.removeprefix("!")
        value = tuple(interactive_shell.dispatch_command(ctx,
                                                         interactive_shell.interactive_shell,
                                                         " ".join(value)).split(" "))
        if len(value) == 0 or value[0] == "":
            common_utils.print_warning("Command returned nothing, aborting")
            return None
    value_str = " ".join(value).strip()
    if variables.global_vars.has_variable(name):
        # Scenario one
        info = variables.global_vars.get_variable_info(name)
        new_value: variable_manager.VariableType
        match str(info.var_type.__name__):
            case "str":
                new_value = value_str
                if len(new_value) > info.length and info.length != -1:
                    common_utils.print_error(
                        f"'{value_str}' is too large to fit the variable")

                    return None
            case "bool":
                # It must be convertible into a bool
                match value_str.lower():
                    case "1" | "true" | "on":
                        new_value = True
                    case "0" | "false" | "off":
                        new_value = False
                    case "!":
                        new_value = not variables.global_vars.get_variable(
                            name)
                    case _:
                        common_utils.print_error(
                            f"'{value}' is not a valid boolean")
                        return None
            case "int":
                # It must be convertible into an int
                try:
                    new_value = int(value_str)
                except ValueError:
                    common_utils.print_error(
                        f"'{value_str}' is not a valid integer")
                    return None
            case "list":
                new_value = value_str.split(";")
                if len(new_value) > info.length and info.length != -1:
                    common_utils.print_error(
                        f"'{value_str}' is too large to fit the variable")
                    return None
            case _:
                raise common_utils.UserError(
                    "Invalid type found as variable's type")
        variables.global_vars.set_variable(name, new_value, -1, "")
        common_utils.print_info(
            f"[blue]{name}[/blue][green] =>[/green]", rich.pretty.Pretty(new_value))
    else:
        variables.global_vars.set_variable(name, value_str, -1, "")
        common_utils.print_info(
            f"[blue]{name}[/blue][green] =>[/green]", rich.pretty.Pretty(value_str))
    return None
