"""
Shell variables
"""
from snr.core.core import variable_manager

__all__ = (
    "global_vars",
)

global_vars = variable_manager.VariableManager()
