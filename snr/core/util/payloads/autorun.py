"""
Module containing a class providing support for automatically
running executables on boot while preserving order
"""
import os
import os.path
import pprint

from snr.core.core import context
from snr.core.util import common_utils, programs
from snr.core.util.payloads import systemd_service, systemd_target

__all__ = (
    "Autorun",
)

class Autorun:
    """Providing support for automatically running executables on boot while preserving order
    """
    _services: list[systemd_service.SystemdService] = []
    _custom_target: systemd_target.SystemdTarget
    _context: context.Context

    def __init__(self, ctx: context.Context):
        common_utils.print_debug("Autorun instance created")
        snr_target = systemd_target.SystemdTarget(ctx, "snr")
        snr_target.Unit_section["Description"] = "Snr boot target"
        snr_target.Unit_section["Requires"] = "multi-user.target"
        snr_target.Unit_section["After"] = "multi-user.target"
        self._custom_target = snr_target
        self._context = ctx

    def add_executable(self, path: str, name: str | None = None) -> 'Autorun':
        """Add an executable to be executed to the systemd configuration
        
        Args:
            path: Path to the executable
            name: Name of the service
        
        Returns:
            The class instance itself. This is done for convenience
        """
        service = systemd_service.SystemdService(self._context, os.path.basename(
            path.split(" ", maxsplit=1)[0]) if name is None else name)
        service.Unit_section["Description"] = f"Autorun service for {path}"
        service.Service_section["ExecStart"] = path
        service.Service_section["Type"] = "simple"
        service.Service_section["ExecRestart"] = "/usr/bin/true"
        service.Service_section["ExecStop"] = "/usr/bin/true"
        service.Service_section["StandardInput"] = "tty"
        service.Service_section["StandardOutput"] = "tty"
        service.Service_section["TTYPath"] = "/dev/tty1"
        service.Install_section["RequiredBy"] = "snr.target"
        if len(self._services) > 1:
            common_utils.print_debug(
                f"Service is to be executed after {self._services[-1].basename}")
            # Preserve the original order
            service.Service_section["After"] = self._services[-1].basename
            service.Service_section["Requires"] = self._services[-1].basename
        if os.path.exists(os.path.join(self._context.root_directory, path)):
            errorcode = programs.Chmod().invoke_and_wait(
                None, "+x", self._context.join(path))
            if errorcode != 0:
                common_utils.print_debug(
                    "Marking service executable as +x failed")
        else:
            common_utils.print_debug(
                "Skipping making service executable as +x due to the executable not existing")
        self._services.append(service)
        common_utils.print_debug(
            "New service added:\n"
            f"Unit: {pprint.pformat(service.Unit_section)}\n"
            f"Service: {pprint.pformat(service.Service_section)}\n"
            f"Install:{pprint.pformat(service.Install_section)}")
        return self

    def write(self) -> None:
        """Write the systemd configuration to the target
        """
        target_requires = "".join(
            [service.basename for service in self._services])
        # Update the Requires entry of snr.target
        self._custom_target.Unit_section["Requires"] = target_requires
        # Create the snr target and link it as the default one
        self._custom_target.write()
        try:
            os.remove(os.path.join(systemd_service.SYSTEMD_SYSTEM_PATH(
                self._context), "default.target"))
        except FileNotFoundError:
            pass
        os.symlink("snr.target", os.path.join(systemd_service.SYSTEMD_SYSTEM_PATH(self._context),
                                              "default.target"))
        snr_target_requires_dir = os.path.join(systemd_service.SYSTEMD_SYSTEM_PATH(self._context),
                                               "snr.target.requires")
        for service in self._services:
            service.write(False, False)
            os.symlink(os.path.join("..", service.basename),
                       os.path.join(snr_target_requires_dir,
                                    service.basename))
