"""
Payload class base
"""

import os.path
import shutil
from typing import Mapping, Optional

from snr.cli import variables
# This is an exception to the general rule, it is best for payloads to
# get their Context class from payload, so they can use that name for `snr.core.payload.context`
from snr.core.core.context import Context
from snr.core.core.variable_manager import VariableType
from snr.core.util import at_formatter, common_utils
from snr.core.util.payloads import autorun

__all__ = (
    "Payload", "Context"
)


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

        ROOTFS_VERSION: Ask for a specific rootfs version, if snr is running an earlier version, it will patch it's rootfs up
    """
    AUTHORS: tuple[Optional[str], ...] = ()
    LICENSE: str = "gpl-3.0"
    INPUTS: tuple[tuple[str, VariableType, int, str] |
                  tuple[str, VariableType, int, str, bool], ...] = ()
    DEPENDENCIES: tuple[str, ...] = ()
    TARGET_OS_LIST: tuple[str, ...] = ()
    ROOTFS_VERSION: int

    _autorun: autorun.Autorun | None = None

    def load(self) -> int:
        """Payload load hook

        Returns:
            status code (0 for success, anything else for failure)
        """
        for inp in self.INPUTS:
            if len(inp) == 4:
                variables.global_vars.set_variable(
                    inp[0], inp[1], inp[2], inp[3], True)
            elif len(inp) == 5:
                variables.global_vars.set_variable(
                    inp[0], inp[1], inp[2], inp[3], True, inp[4])
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

    def generate(self, ctx: Context) -> int:
        """Payload generate method

        Args:
            ctx: Payload generation context

        Returns:
            status code (0 for success, anything else for failure)
        """
        raise NotImplementedError

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

    def format_payload_and_write(self, ctx: Context, data: Mapping[str, VariableType],
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
        result = {}
        for inp in self.INPUTS:
            result[inp[0]] = variables.global_vars.get_variable(inp[0])
            var_info = variables.global_vars.get_variable_info(inp[0])
            if var_info.required and result[inp[0]] == var_info.default_value:
                raise common_utils.UserError(
                    f"{inp[0]} is required but is not set")
        return result

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
