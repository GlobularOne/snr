"""
Wrap a program to be executed inside a chroot environment
"""
from typing import Callable

from snr.core.core import context
from snr.core.util import program_wrapper
from snr.core.util.program_wrapper import (DEVNULL, PIPE, STDOUT,
                                           SubprocessError)

__all__ = (
    "DEVNULL", "PIPE",
    "STDOUT", "SubprocessError",
    "chroot_program_wrapper_factory",
)


def chroot_program_wrapper_factory(program_name: str) \
        -> Callable[[context.Context], type[program_wrapper.ProgramWrapperBase]]:
    """Factory function for ProgramWrapperBase that uses the chroot

    Args:
        program_name: Name of the program to wrap

    Returns:
        A callable function that should be called with just the context,
        and it returns a ChrootProgramWrapper instance wrapping
        the passed program at the passed context
    """
    def inner_factory(ctx: context.Context) -> type[program_wrapper.ProgramWrapperBase]:
        class CustomProgramWrapper(program_wrapper.ProgramWrapperBase,
                                   interpreter=("chroot", ctx.root_directory),
                                   program=program_name):
            """Wrap {0} inside a real chroot context"""
        class_name = f"{program_name.title()}ChrootWrapper"
        class_name = class_name.replace("-", "").replace("_", "")
        CustomProgramWrapper.__name__ = class_name
        assert CustomProgramWrapper.__doc__ is not None
        CustomProgramWrapper.__doc__ = CustomProgramWrapper.__doc__.format(
            program_name)
        return CustomProgramWrapper
    inner_factory.__name__ = program_name.lower().replace("-", "_") + "_factory"
    return inner_factory
