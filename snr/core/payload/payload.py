"""
Payload class base
"""

import ipaddress
import os.path
import re
import shutil
import socket
from typing import Any, Mapping, Optional

from snr.cli import variables
# This is an exception to the general rule, it is best for payloads to
# get their Context class from payload, so they can use that name for `snr.core.payload.context`
from snr.core.core.context import Context
from snr.core.core.variable_manager import (NORMAL, REQUIRED, USED_BY_PAYLOAD,
                                            VALID_ALPHA, VALID_ALPHANUM,
                                            VALID_ASCII, VALID_HOST_PATH,
                                            VALID_IP, VALID_IPV4, VALID_IPV6,
                                            VALID_LOCAL_PATH,
                                            VALID_PATH_COMPONENT, VALID_PORT,
                                            VALID_STRING, VariableFlags,
                                            VariableType)
from snr.core.util import at_formatter, common_utils, network_interfaces
from snr.core.util.payloads import autorun

__all__ = (
    "Payload", "Context",
    "NORMAL", "REQUIRED",
    "USED_BY_PAYLOAD", "VALID_STRING",
    "VALID_ALPHA", "VALID_ALPHANUM",
    "VALID_ASCII", "VALID_PATH_COMPONENT",
    "VALID_LOCAL_PATH", "VALID_HOST_PATH",
    "VALID_PORT", "VALID_IP",
    "VALID_IPV4", "VALID_IPV6"
)

_invalid_path_chars = re.compile(r'[<>:"/\\|?*]')


class Payload:
    """Base payload class. Contains utilities for payload generation as well.

    Attributes:

        AUTHORS:
            Tuple of authors. In format "Pseudonym (Real name) <Email>".
            In place of pseudonym, real name can be used and all parts but the name is optional

        LICENSE:
            License SPDX identifier, not specifying one means using
            the project's license (GPLv3)

        INPUTS:
            A tuple of input variables. More specifically, it's a tuple of tuples,
            each tuple is for one variable. Order is, variable name,
            default value, size, documentation An example would be:
            (
                ("foo", "bar", 3, "Foo or bar"),
                ("spam", [], 12, "12 Spams")
            )

        DEPENDENCIES: Deb packages as dependencies for the payload to work

        ROOTFS_VERSION: Ask for a specific rootfs version, if snr is running 
                        an earlier version, it will patch it's rootfs up
    """
    AUTHORS: tuple[Optional[str], ...] = ()
    LICENSE: str = "gpl-3.0"
    INPUTS: tuple[tuple[str, VariableType, int, str] |
                  tuple[str, VariableType, int, str, bool] |
                  tuple[str, VariableType, int, str, VariableFlags], ...] = ()
    DEPENDENCIES: tuple[str, ...] = ()
    TARGET_OS_LIST: tuple[str, ...] = ()
    ROOTFS_VERSION: int

    _autorun: autorun.Autorun | None = None
    _validated_vars: dict[str, VariableType]

    @staticmethod
    def _validate_str_var(name: str, value: str, flags: VariableFlags, ctx: Context) -> str:
        for flag in flags:
            match flag:
                case VariableFlags.VALID_STRING:
                    if len(value.strip()) == 0 or "\x00" in value:
                        raise common_utils.UserError(
                            f"{name} may not be empty or contain null bytes")
                case VariableFlags.VALID_ALPHA:
                    if value.isalpha():
                        raise common_utils.UserError(
                            f"{name} must be alphabetic")
                case VariableFlags.VALID_ALPHANUM:
                    if value.isalnum():
                        raise common_utils.UserError(
                            f"{name} must be alphabetic-numeric")
                case VariableFlags.VALID_ASCII:
                    if value.isascii():
                        raise common_utils.UserError(
                            f"{name} must be ASCII")
                case VariableFlags.VALID_PATH_COMPONENT:
                    if _invalid_path_chars.search(value):
                        raise common_utils.UserError(
                            f"{name} must be a valid path component")
                case VariableFlags.VALID_LOCAL_PATH:
                    if not os.path.exists(value):
                        raise common_utils.UserError(
                            f"{name} does not exist on the local machine")
                case VariableFlags.VALID_HOST_PATH:
                    if not ctx.exists(value):
                        raise common_utils.UserError(
                            f"{name} does not exist on the host machine")
                case VariableFlags.VALID_PORT:
                    common_utils.print_warning(
                        "This is a warning for developers, VALID_PORT cannot be used with strings,"
                        "for a port use an integer variable instead")
                case VariableFlags.VALID_IP | VariableFlags.VALID_IPV4:
                    try:
                        ipaddress.ip_address(value)
                    except ValueError:
                        common_utils.print_debug(
                            f"{name} does not seem to be an IP address, we will try to resolve it")
                        try:
                            new_value = socket.gethostbyname(value)
                        except socket.gaierror:
                            # Last resort, see if it's a valid network interface
                            net_if = network_interfaces.get_network_interface(
                                value)
                            if net_if is None:
                                raise common_utils.UserError(
                                    f"{name} is not a valid IP address, neither a valid"
                                    "hostname nor a valid interface") from None
                            if flag & VariableFlags.VALID_IP:
                                tmp = net_if.ipv4_address if net_if.ipv4_address is None else net_if.ipv6_address
                                if tmp is None:
                                    # No IP capability at all
                                    raise common_utils.UserError(
                                        f"Network interface {name} does not have IP capabilities") from None
                                new_value = tmp
                            else:
                                if net_if.ipv4_address is None:
                                    raise common_utils.UserError(
                                        f"Network interface {name} does not have IPv4 capabilities") from None
                                new_value = net_if.ipv4_address
                        value = new_value
                case VariableFlags.VALID_IPV6:
                    try:
                        ipaddress.ip_address(value)
                    except ValueError:
                        common_utils.print_debug(
                            f"{name} does not seem to be an IPv6 address, we will try to resolve it")
                        try:
                            new_value = socket.getaddrinfo(
                                value, None, socket.AF_INET6)[0][4][0]
                        except (socket.gaierror, IndexError):
                            net_if = network_interfaces.get_network_interface(
                                value)
                            if net_if is None:
                                raise common_utils.UserError(
                                    f"{name} is not a valid IPv6 address, neither a valid hostname"
                                    "nor a valid interface") from None
                            if net_if.ipv6_address is None:
                                raise common_utils.UserError(
                                    f"Network interface {name} does not have IPv6 capabilities") from None
                            new_value = net_if.ipv6_address
                        value = new_value
        return value

    @staticmethod
    def _validate_int_var(name: str, value: int, flags: VariableFlags, _: Context) -> int:
        for flag in flags:
            match flag:
                case VariableFlags.VALID_PORT:
                    if value not in range(0, 65535):
                        raise common_utils.UserError(
                            f"{name} is not a valid port number"
                        )
        return value

    def load(self) -> int:
        """Payload load hook

        Returns:
            status code (0 for success, anything else for failure)
        """
        for inp in self.INPUTS:
            if len(inp) == 4:
                variables.global_vars.set_variable(
                    inp[0], inp[1], inp[2], inp[3], USED_BY_PAYLOAD)
            elif len(inp) == 5:
                flags = inp[4]
                if isinstance(flags, bool):
                    flags = VariableFlags(flags)
                variables.global_vars.set_variable(
                    inp[0], inp[1], inp[2], inp[3], USED_BY_PAYLOAD | flags)
            else:
                raise common_utils.UserError(
                    f"'{inp}' is not a valid input variable")
        return 0

    def unload(self) -> int:
        """Payload unload hook

        Returns:
            status code (0 for success, anything else for failure)
        """
        for inp in self.INPUTS:
            variables.global_vars.del_variable(inp[0])
        return 0

    def validate(self, ctx: Context) -> dict[str, VariableType]:
        """Validate variables

        Raises:
            common_utils.UserError: One of the condition of variables failed

        Returns:
            All related variables
        """
        result = {}
        for inp in self.INPUTS:
            value = variables.global_vars.get_variable(inp[0])
            result[inp[0]] = value
            var_info = variables.global_vars.get_variable_info(inp[0])
            if var_info.flags & REQUIRED and result[inp[0]] == var_info.default_value:
                raise common_utils.UserError(
                    f"{inp[0]} is required but is not set")
            if isinstance(value, str):
                result[inp[0]] = self._validate_str_var(
                    inp[0], value, var_info.flags, ctx)
            elif isinstance(value, int):
                result[inp[0]] = self._validate_int_var(
                    inp[0], value, var_info.flags, ctx)
            elif isinstance(value, list):
                new_value = []
                for index, element in enumerate(value):
                    new_value.append(self._validate_str_var(
                        inp[0] + f"[{index}]", element, var_info.flags, ctx))
        self._validated_vars = result
        return result

    def generate(self, ctx: Context) -> int:
        """Payload generate method

        Args:
            ctx: Payload generation context

        Returns:
            status code (0 for success, anything else for failure)
        """
        raise NotImplementedError

    @staticmethod
    def supports_encrypted_access() -> tuple[str, list[str], int, str]:
        """Declare that the payload supports decrypting partitions

        It does so with declaring a PASSPHRASES string list variable
        you could use with many utilities of snr to access encrypted partitions

        Returns:
            The variable definitions you need to add
        """
        return ("PASSPHRASES", [], -1, "Passphrases to try for encrypted partitions")

    def copy_root_to_root(self, ctx: Context, module_path: str,
                          src: str, dest: str,
                          follow_symlinks: bool = True) -> str:
        """Copy a file from payload's package root to host filesystem's root

        Args:
            ctx: Payload generation context
            module_path: Path to the payload's __init__.py module
            src: copy operation source
            dest: copy operation destination
            follow_symlinks Follow symlinks instead of recreating them. Defaults to True

        Returns:
            Destination path
        """
        return shutil.copyfile(os.path.join(os.path.dirname(module_path), src),
                               ctx.join(dest),
                               follow_symlinks=follow_symlinks)

    def format_payload_and_write(self, ctx: Context, data: Mapping[str, Any],
                                 local_payload_path: str = "payload.py",
                                 host_payload_path: str = "root/payload.py") -> None:
        """Format a payload using AtFormatter and write it to the host filesystem

        Args:
            ctx: Payload generation context
            data: Variable, Value dictionary
            local_payload_path: Local path to payload
            host_payload_path: Path inside the host filesystem to write the result to
        """
        with open(local_payload_path, encoding="utf-8") as stream:
            payload_data = stream.read()
        with common_utils.rootfs_open(ctx, host_payload_path, "w") as stream:
            stream.write(at_formatter.AtFormatter(
                data).format_str(payload_data))

    def get_self_variables(self) -> dict[str, VariableType]:
        """Obtain all variables related to this payload.
        Variables related to this payload are discovered using the payload's INPUTS

        Returns:
            All variables related to this payload
        """
        return self._validated_vars

    def add_autorun(self, ctx: Context, executable: str = "root/payload.py") -> None:
        """Add an autorun service for executable.
        In case of several calls, order will be preserved

        Args:
            ctx: Payload generation context
            executable: Executable to add service for (it must exist on host filesystem)
        """
        if self._autorun is None:
            self._autorun = autorun.Autorun(ctx)
        self._autorun.add_executable(executable).write()
