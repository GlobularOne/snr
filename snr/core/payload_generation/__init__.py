"""
Payload generation core functionality
"""
from typing import Callable

from snr.core.core import context
from snr.core.payload import safety_pin
from snr.core.payload_generation.post import (core_configuration, finishing,
                                              grub_installation)
from snr.core.payload_generation.pre import (ensuring_dependencies, formatting,
                                             host_check, partitioning,
                                             rootfs_preparation)

__all__ = (
    "payload_generation_pre", "payload_generation_post"
)


def _call_step(func: Callable[[context.Context], bool], ctx: context.Context) -> None:
    return_value = func(ctx)
    if not return_value:
        raise RuntimeError(f"Step failed with return code: {return_value}")


def payload_generation_pre(ctx: context.Context) -> bool:
    """Do pre payload generation steps

    Args:
        ctx: Context

    Returns:
        Whatever the steps were successful or not
    """
    try:
        _call_step(host_check.check_host, ctx)
        _call_step(partitioning.partition_host, ctx)
        _call_step(formatting.format_host, ctx)
        _call_step(rootfs_preparation.prepare_rootfs, ctx)
        _call_step(ensuring_dependencies.ensure_dependencies, ctx)
    except RuntimeError:
        return False
    return True


def payload_generation_post(ctx: context.Context, verbosity: str) -> bool:
    """Do post payload generation steps

    Args:
        ctx: Context
        verbosity: Either "normal", "quiet", "verbose" or "debug"

    Returns:
        Whatever the steps were successful or not
    """
    safety_pin.remove_safety_pin(ctx.root_directory)
    try:
        core_configuration.configure_core(ctx, verbosity)
        grub_installation.install_grub(ctx)
        finishing.finish_host(ctx)
        _call_step(rootfs_preparation.prepare_rootfs, ctx)
        _call_step(ensuring_dependencies.ensure_dependencies, ctx)
    except RuntimeError:
        return False
    return True
