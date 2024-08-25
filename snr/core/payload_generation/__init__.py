"""
Payload generation core functionality
"""
from typing import Any, Callable, Generator

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


def _call_step(func: Callable[..., bool], *args: Any) -> None:
    return_value = func(*args)
    if not return_value:
        raise RuntimeError(f"Step failed with return code: {return_value}")


def payload_generation_pre(ctx: context.Context) -> Generator[int, int, bool]:
    """Do pre payload generation steps

    Args:
        ctx: Context

    Returns:
        Whatever the steps were successful or not
    """
    yield 5
    try:
        _call_step(host_check.check_host, ctx)
        yield 1
        _call_step(partitioning.partition_host, ctx)
        yield 2
        _call_step(formatting.format_host, ctx)
        yield 3
        _call_step(rootfs_preparation.prepare_rootfs, ctx)
        yield 4
        _call_step(ensuring_dependencies.ensure_dependencies, ctx)
        yield 5
    except RuntimeError:
        return False
    return True


def payload_generation_post(ctx: context.Context, verbosity: str) -> Generator[int, int, bool]:
    """Do post payload generation steps

    Args:
        ctx: Context
        verbosity: Either "normal", "quiet", "verbose" or "debug"

    Returns:
        Whatever the steps were successful or not
    """
    safety_pin.remove_safety_pin(ctx.root_directory)
    yield 1
    try:
        _call_step(core_configuration.configure_core, ctx, verbosity)
        yield 2
        _call_step(grub_installation.install_grub, ctx)
        yield 3
        _call_step(finishing.finish_host, ctx)
        yield 4
        _call_step(rootfs_preparation.prepare_rootfs, ctx)
        yield 5
        _call_step(ensuring_dependencies.ensure_dependencies, ctx)
        yield 6
    except RuntimeError:
        return False
    return True
