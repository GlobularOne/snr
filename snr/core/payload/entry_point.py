"""
Entry point that handles snr core initialization, data_dir, debug mode and safety pin
"""

from typing import Callable

from snr.core.payload import data_dir, safety_pin
from snr.core.util import common_utils

__all__ = (
    "entry_point",
)


def entry_point(func: Callable[[], None]) -> Callable[[], None]:
    """Payload entry point decorator

    Args:
        func: Payload entry point
    """

    def inner_entry_point() -> None:
        """Inner entry point
        """
        safety_pin.require_lack_of_safety_pin()
        data_dir.fix_data_dir()
        try:
            func()
        except Exception:  # pylint: disable=broad-exception-caught
            common_utils.handle_exception()

    return inner_entry_point
