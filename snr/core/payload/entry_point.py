"""
Entry point that handles snr core initialization, data_dir, storage setup, debug mode and safety pin
"""

import inspect
from typing import Callable

from snr.core.payload import context, data_dir, safety_pin, storage
from snr.core.util import common_utils

__all__ = (
    "entry_point",
)

EntryPointType = Callable[[
    list[storage.BlockInfo], context.Context, str], None] | Callable[[], None]


def entry_point(func: EntryPointType | None = None,
                no_lvm: bool = False):
    """Payload entry point decorator

    Args:
        func: Payload entry point
        no_lvm: Do not discover LVM partitions
    """

    def execute_payload(func: EntryPointType) -> None:
        """Execute the payload function with necessary setup."""
        safety_pin.require_lack_of_safety_pin()
        data_dir.fix_data_dir()
        try:
            payload_name = getattr(
                inspect.getmodule(func), "__doc__", "Payload") or "Payload"
            payload_name.strip()
            common_utils.print_debug(f"{payload_name} started")
            if len(inspect.signature(func).parameters) > 0:
                block_info, root_ctx, our_device = storage.setup(no_lvm=no_lvm)
                func(block_info, root_ctx, our_device)
            else:
                func()
            common_utils.print_ok(f"{payload_name} completed")
        except Exception as exc:  # pylint: disable=broad-exception-caught
            common_utils.handle_exception()

    if func is not None:
        return lambda: execute_payload(func)
    return lambda f: lambda: execute_payload(f)
