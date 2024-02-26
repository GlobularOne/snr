"""
Snr interactive environment commands
"""
from libsnr.util.common_utils import print_debug as _print_debug

from snr.commands.filesystem import *
from snr.commands.misc import *
from snr.commands.payload import *
from snr.commands.variable import *


def discover_commands():
    """
    Discover all commands
    """
    commands = {}
    for name, obj in globals().items():
        if name.startswith("cmd_"):
            _print_debug(f"Discovered command \'{name.removeprefix('cmd_')}\'")
            commands[name.removeprefix("cmd_")] = obj
    return commands
