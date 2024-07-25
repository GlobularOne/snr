"""
Format a string, replacing "@variable@" with value
"""

from typing import Mapping, Any

__all__ = (
    "AtFormatter",
)


class AtFormatter:  # pylint: disable=too-few-public-methods
    """Format a string, replacing "@variable@" with value
    """
    variables: Mapping[str, Any]

    def __init__(self, preset: Mapping[str, Any] | None = None):
        if preset is not None:
            self.variables = dict(preset.items())

    def format_str(self, string: str) -> str:
        """Formats a string according to the variables

        Args:
            string: The string to format.

        Returns:
            The formatted string with variables
        """
        for var, value in self.variables.items():
            if f"\"@{var}@\"" in string:
                string = string.replace(f"@{var}@", repr(value))
        return string
