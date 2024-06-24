"""
Console wrappers
"""

import rich.console

__all__ = (
    "console", "err_console"
)


console = rich.console.Console()

err_console = rich.console.Console(stderr=True)
