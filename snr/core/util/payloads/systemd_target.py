"""
Module containing a class providing systemd target file support
"""

from snr.core.util.payloads import systemd_unit
from snr.core.util.payloads.systemd_unit import \
    SYSTEMD_SYSTEM_PATH

__all__ = (
    "SYSTEMD_SYSTEM_PATH", "SystemdTarget"
)


class SystemdTarget(systemd_unit.SystemdUnit, suffix=".target", extra_sections=()):
    """Provide systemd target file support
    """
