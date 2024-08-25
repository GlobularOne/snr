"""
Shell variables
"""
from snr.core.core import variable_manager
from snr.core.core.variable_manager import (NORMAL, REQUIRED, USED_BY_PAYLOAD,
                                            VALID_ALPHA, VALID_ALPHANUM,
                                            VALID_ASCII, VALID_HOST_PATH,
                                            VALID_PORT, VALID_IP,
                                            VALID_IPV4, VALID_IPV6,
                                            VALID_LOCAL_PATH,
                                            VALID_PATH_COMPONENT, VALID_STRING)

__all__ = (
    "global_vars", "NORMAL",
    "REQUIRED", "USED_BY_PAYLOAD",
    "VALID_STRING", "VALID_ALPHA",
    "VALID_ALPHANUM", "VALID_ASCII",
    "VALID_PATH_COMPONENT", "VALID_LOCAL_PATH",
    "VALID_HOST_PATH", "VALID_PORT",
    "VALID_IP", "VALID_IPV4",
    "VALID_IPV6"
)

global_vars = variable_manager.VariableManager()
