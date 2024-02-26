"""
Variable-related commands
"""
from libsnr.util.common_utils import Table as _Table
from libsnr.util.common_utils import print_error as _print_error
from libsnr.util.common_utils import print_warning as _print_warning

from snr.command_utils import dispatch_command as _dispatch_command
from snr.variables import global_vars as _global_vars


def cmd_unset(argv: list[str], argc: int):
    """\
Unset a variable
    """
    if argc == 0:
        _print_error("unset requires an argument")
        return
    if not _global_vars.has_variable(argv[0]):
        _print_error(f"No variable named '{argv[0]}'")
        return
    _global_vars.del_variable(argv[0])


def cmd_set(argv: list[str], argc: int):  # pylint: disable=too-many-return-statements
    """\
Set value of a variable (syntax: set <variable name> <value>).
Or unset a variable (syntax: set <variable name>).
Or list all variables (syntax: set)
    """
    if argc == 0:
        table = _Table("Variables")
        table.add_row(
            "Name",
            "Type",
            "Length limit",
            "Value")
        for name, info in zip(_global_vars.get_variables_name(),
                              _global_vars.get_variables_info()):
            var_type = str(info.var_type.__name__)
            var_len = str(info.length) if info.length != -1 else "unlimited"
            value = _global_vars.get_variable(name)
            if isinstance(value, list):
                value = " ".join(map(str, value))
            else:
                value = str(value)
            table.add_row(name, var_type, var_len, value)
        return str(table)
    if argc == 1:
        # set <variable name> == unset <variable name>
        _global_vars.del_variable(argv[0])
        return None
    # Two scenarios are possible:
    #   1. The variable already exists, so already has type information
    #   2. The variable doesn't exist, so type is str
    name, value = argv[0], " ".join(argv[1:])
    if name.startswith("!"):
        # The value is a command to execute
        name = name.removeprefix("!")
        value = _dispatch_command(value)
        if value is None:
            _print_warning("Command returned nothing, aborting")
            return None
        value = value.strip()
    if _global_vars.has_variable(name):
        # Scenario one
        info = _global_vars.get_variable_info(name)
        match str(info.var_type.__name__):
            case "str":
                new_value = value
                if len(new_value) > info.length and info.length != -1:
                    _print_error(
                        f"'{value}' is too large to fit the variable")
                    return None
            case "bool":
                # It must be convertible into a bool
                match value.lower():
                    case "1" | "true" | "on":
                        new_value = True
                    case "0" | "false" | "off":
                        new_value = False
                    case _:
                        _print_error(f"'{value}' is not a valid boolean")
                        return None
            case "int":
                # It must be convertible into an int
                try:
                    new_value = int(value)
                except ValueError:
                    _print_error(f"'{value}' is not a valid integer")
                    return None
            case "list":
                new_value = value.split(";")
                if len(new_value) > info.length and info.length != -1:
                    _print_error(
                        f"'{value}' is too large to fit the variable")
                    return None
            case _:
                raise ValueError("Invalid type found as variable's type")
        _global_vars.set_variable(name, new_value, -1, "")
    else:
        _global_vars.set_variable(name, value, -1, "")
        return None
