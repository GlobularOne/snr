"""
Variable manager, containing methods to set, get and delete variables
"""
import dataclasses
import enum
import warnings

__all__ = (
    "VariableType", "VariableTypeType",
    "VariableTypesTuple", "VariableInfo",
    "VariableManager", "NORMAL",
    "REQUIRED", "USED_BY_PAYLOAD",
    "VALID_STRING", "VALID_ALPHA",
    "VALID_ALPHANUM", "VALID_ASCII",
    "VALID_PATH_COMPONENT", "VALID_LOCAL_PATH",
    "VALID_HOST_PATH", "VALID_PORT",
    "VALID_IP", "VALID_IPV4",
    "VALID_IPV6"
)

# Type that matches all possible variable types
VariableType = str | int | bool | list[str]
# Type of type that matches all possible variable types
VariableTypeType = type[str | int | bool | list[str]]
# Tuple that matches all possible variable types
VariableTypesTuple = (str, int, bool, list)


class VariableFlags(enum.Flag):
    """
    Flag variables
    """
    NORMAL = 0
    REQUIRED = enum.auto()
    USED_BY_PAYLOAD = enum.auto()
    VALID_STRING = enum.auto()
    VALID_STR_ALPHA = enum.auto()
    VALID_STR_ALPHANUM = enum.auto()
    VALID_STR_ASCII = enum.auto()
    VALID_STR_PATH_COMPONENT = enum.auto()
    VALID_STR_LOCAL_PATH = enum.auto()
    VALID_STR_HOST_PATH = enum.auto()
    VALID_PORT = enum.auto()
    VALID_IP = enum.auto()
    VALID_IPV4 = enum.auto()
    VALID_IPV6 = enum.auto()
    VALID_ALPHA = VALID_STRING | VALID_STR_ALPHA
    VALID_ALPHANUM = VALID_STRING | VALID_STR_ALPHANUM
    VALID_ASCII = VALID_STRING | VALID_STR_ASCII
    VALID_PATH_COMPONENT = VALID_STRING | VALID_STR_PATH_COMPONENT
    VALID_LOCAL_PATH = VALID_STRING | VALID_STR_LOCAL_PATH
    VALID_HOST_PATH = VALID_STRING | VALID_STR_HOST_PATH


# Variable does not need any special treatment
NORMAL = VariableFlags.NORMAL
# Variable is required
REQUIRED = VariableFlags.REQUIRED
# Variable is used by a payload and should not be removed by shell commands
USED_BY_PAYLOAD = VariableFlags.USED_BY_PAYLOAD
# Value must be non-empty, and not be made of entirely whitespace and not contain null bytes
VALID_STRING = VariableFlags.VALID_STRING
# Value must be a valid [a-zA-Z]
VALID_ALPHA = VariableFlags.VALID_ALPHA
# Value must be a valid [a-zA-Z0-9]
VALID_ALPHANUM = VariableFlags.VALID_ALPHANUM
# Value must be a valid ASCII string
VALID_ASCII = VariableFlags.VALID_ASCII
# Value must be a valid path component
VALID_PATH_COMPONENT = VariableFlags.VALID_PATH_COMPONENT
# Value must be an existing, readable path in the local machine
VALID_LOCAL_PATH = VariableFlags.VALID_LOCAL_PATH
# Value must be an existing, readable path in the host machine
VALID_HOST_PATH = VariableFlags.VALID_HOST_PATH
# Value must be a valid port number
VALID_PORT = VariableFlags.VALID_PORT
# Value must be a valid IP (Whatever  IPv4 or IPv6)
VALID_IP = VariableFlags.VALID_IP
# Value must be a valid IPv4
VALID_IPV4 = VariableFlags.VALID_IPV4
# Value must be a valid IPv6
VALID_IPV6 = VariableFlags.VALID_IPV6


@dataclasses.dataclass
class VariableInfo:  # pylint: disable=too-few-public-methods
    """Variable's info
    """
    description: str = ""
    length: int = -1
    var_type: VariableTypeType = str
    flags: VariableFlags = NORMAL
    default_value: VariableType | None = None


class VariableManager:
    """Variable manager, containing methods to set, get and delete variables
    """
    _variables: dict[str, tuple[VariableType, VariableInfo]]
    _VariableValueType = tuple[VariableType, VariableInfo]

    def __init__(self,
                 pre: dict[str, _VariableValueType] | None = None):
        if pre is None:
            self._variables = {}
        else:
            self._variables = {**pre}

    def __repr__(self) -> str:
        return f"{type(self).__name__}({repr(self._variables)})"

    def has_variable(self, name: str) -> bool:
        """Check if variable is defined

        Args:
            name: Name of variable to check

        Returns:
            True if variable is defined False
        """
        return name in self._variables

    def set_variable(self, name: str, value: VariableType,
                     info_length: int = -1, info_description: str = "",
                     flags: VariableFlags = VariableFlags.NORMAL) -> None:
        """Set value of variable.

        Args:
            name: Name of variable to set
            value: Value of variable
            info_length: Length of variable if -1 no length will be set
            info_description: Description of variable
            flags: Flags for the variable
        """
        if isinstance(value, VariableTypesTuple):
            if isinstance(value, list):
                for i, element in enumerate(value):
                    if not isinstance(element, VariableTypesTuple):
                        raise ValueError(
                            f"Unsupported type of value[{i}]")
                value = list(value)
        else:
            raise ValueError(f"Unsupported type '{type(value)}'")

        if type(value) in (int, bool) and info_length != -1:
            warnings.warn("Variables of integer types cannot have length")
            info_length = -1

        if name in self._variables and not flags & USED_BY_PAYLOAD:
            info = self._variables[name][1]
            if not isinstance(value, info.var_type):
                raise TypeError(
                    f"'{value}' is not of type defined for variable")
            if info.length != -1 and isinstance(value, (str, list)):
                if len(value) > info.length:
                    warnings.warn(
                        f"Value does not fit the size ({info.length})")
                    info_length = -1
            if info_length != -1:
                info.length = info_length
            if len(info_description) == 0:
                info.description = info_description
        else:
            info = VariableInfo()
            info.length = info_length
            info.description = info_description
            info.var_type = type(value)
            info.flags = flags
            if flags & USED_BY_PAYLOAD:
                info.default_value = value
        self._variables[name] = (value, info)

    def del_variable(self, name: str) -> None:
        """Delete a variable from the variable map

        Args:
            name: Name of the variable to delete
        """
        if name in self._variables:
            del self._variables[name]

    def get_variable(self, name: str) -> VariableType:
        """Get the variable with the given name

        Args:
            name: The name of the variable to get

        Returns:
            The variable with the given name
        """
        if name in self._variables:
            return self._variables[name][0]
        raise ValueError(f"No variable named '{name}'")

    def get_variable_str(self, name: str) -> str:
        """Get the variable with the given name, interpreting it as a string

        Args:
            name: The name of the variable to get.

        Raises:
            TypeError: The variable is not meant to be interpreted as a string

        Returns:
            The variable with the given name
        """
        if self.get_variable_info(name).var_type != str:
            raise TypeError(
                f"Variable '{name}' is not to be interpreted as a string")
        return str(self.get_variable(name))

    def get_variable_list(self, name: str) -> list[str]:
        """Get the variable with the given name, interpreting it as a string

        Args:
            name: The name of the variable to get.

        Raises:
            TypeError: The variable is not meant to be interpreted as a list

        Returns:
            The variable with the given name
        """
        if self.get_variable_info(name).var_type != list:
            raise TypeError(
                f"Variable '{name}' is not to be interpreted as a list")
        value = self.get_variable(name)
        assert isinstance(value, list)
        return value

    def get_variable_info(self, name: str) -> VariableInfo:
        """Get information about a variable

        Args:
            name: Name of the variable to get information about

        Raises:
            KeyError: Name is not a recognized variable

        Returns:
            Variable information
        """
        if name in self._variables:
            return self._variables[name][1]
        raise KeyError(f"No variable named '{name}'")

    def get_variables_name(self) -> list[str]:
        """Get list of variables names.

        Returns:
            list of variable names
        """
        return list(self._variables.keys())

    def get_variables_value(self) -> list[VariableType]:
        """Get list of variables values.

        Returns:
            list of variable values
        """
        return list(v[0] for v in self._variables.values())

    def get_variables_info(self) -> list[VariableInfo]:
        """Get list of all variable's info

        Returns:
            list of all variable info
        """
        return list(v[1] for v in self._variables.values())
