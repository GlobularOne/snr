"""
Module containing a class providing systemd service file support
"""

from snr.core.util.payloads import systemd_unit
from snr.core.util.payloads.systemd_unit import \
    SYSTEMD_SYSTEM_PATH
from snr.core.util.payloads.systemd_unit import SystemdSectionType

__all__ = (
    "SYSTEMD_SYSTEM_PATH", "SystemdService"
)


class SystemdService(systemd_unit.SystemdUnit,
                     suffix=".service",
                     extra_sections=("Service",)):
    """Provide systemd service file support
    """
    Service_section: SystemdSectionType = {}
