"""
Console wrappers
"""

import rich.console

__all__ = (
    "console", "err_console"
)


# Standard console
console = rich.console.Console()

# Standard console for error
err_console = rich.console.Console(stderr=True)
