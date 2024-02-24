"""
Snr interactive environment commands
"""
from snr.commands.filesystem import *
from snr.commands.misc import *
from snr.commands.payload import *
from snr.commands.variable import *
from libsnr.util.common_utils import print_debug as _print_debug


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
