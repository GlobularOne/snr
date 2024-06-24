"""
Satisfy the reported payload dependencies
"""

from snr.core.core import context, options
from snr.core.payload_generation import common
from snr.core.util import chroot_programs, common_utils

__all__ = (
    "ensure_dependencies",
)


def ensure_dependencies(ctx: context.Context) -> bool:
    """Install dependencies of the payload

    Args:
        ctx: Context

    Returns:
        Whatever operation was successful or not
    """
    assert options.payload_module is not None
    if len(options.payload_module.payload.DEPENDENCIES) != 0:  # pylint: disable=no-member
        dependencies = options.payload_module.payload.DEPENDENCIES  # pylint: disable=no-member
        common_utils.print_debug(
            "Installing dependencies of the payload:" +
            ' '.join(dependencies))
        apt_get = chroot_programs.apt_get_factory(ctx)(
            stdout=chroot_programs.PIPE,
            stderr=chroot_programs.STDOUT,
        )

        errorcode = apt_get.invoke_and_wait(None,
                                            *dependencies,
                                            options={
                                                "quiet": "2"
                                            })
        if errorcode != 0:
            assert apt_get.stdout is not None
            common_utils.print_debug(
                f"Command's output: {apt_get.stdout.read()}")
            return common.clean_and_exit(ctx, "Installing dependencies of payload failed")
    else:
        common_utils.print_debug("Payload has no dependencies, nothing to do")
    return True
