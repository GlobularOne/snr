"""
Clean interface to gshadow entries and a few utility functions
"""
import copy
import os.path

__all__ = (
    "UnixGShadowEntry", "parse_unix_gshadow_line",
    "parse_unix_gshadow_file", "format_unix_gshadow_line",
    "format_unix_gshadow_file"
)


class UnixGShadowEntry:  # pylint: disable=too-many-instance-attributes, too-few-public-methods
    """A shadow group entry

    Attributes:
        group_name: Name of the group
        password: Password of the group
        administrators: List of users that have admin privileges of the group
        members: List of normal members of the group
        locked: Whatever users can use the password to add themselves
          to the group dynamically or not
    """
    group_name: str
    password: str
    administrators: list[str]
    members: list[str]
    locked: bool

    def __init__(self, group_name: str, password: str,  # pylint: disable=too-many-arguments
                 administrators: list[str], members: list[str],
                 locked: bool):
        self.group_name = group_name
        self.password = password
        self.administrators = copy.deepcopy(administrators)
        self.members = copy.deepcopy(members)
        self.locked = locked

    def __str__(self) -> str:
        locked_str = ""
        if self.locked:
            locked_str = "!"
        return f"{self.group_name}:{locked_str}{self.password}:" + \
            f"{','.join(self.administrators)}:{','.join(self.members)}"


def parse_unix_gshadow_line(line: str) -> UnixGShadowEntry:
    """Parse a gshadow line and return a UnixGShadowEntry

    Args:
        line: The line to parse

    Returns:
        The parsed UnixPasswdEntry
    """
    group_name, password, administrators_raw, members_raw = line.split(":", 4)
    administrators = ",".split(administrators_raw)
    members = ",".split(members_raw)
    locked = False
    if password.startswith("!"):
        password = password[1:]
        locked = True
    return UnixGShadowEntry(group_name, password, administrators, members, locked)


def parse_unix_gshadow_file(root: str = "/") -> list[UnixGShadowEntry]:
    """Parse the gshadow file and return list of gshadow objects

    Args:
        root: Root of the directory to look for gshadow file

    Returns:
        list of gshadow objects
    """
    gshadow_file = os.path.join(root, "etc", "gshadow")
    gshadows = []
    with open(gshadow_file, encoding="utf-8") as stream:
        for line in stream.readlines():
            if len(line.strip()) != 0:
                gshadows.append(parse_unix_gshadow_line(line))
    return gshadows


def format_unix_gshadow_line(gshadow: UnixGShadowEntry) -> str:
    """Format a UnixGShadowEntry for use in /etc/gshadow.

    Args:
        gshadow: The UnixGShadowEntry to format.

    Returns:
        The formatted string representation of the UnixGShadowEntry
    """
    return str(gshadow)


def format_unix_gshadow_file(gshadows: list[UnixGShadowEntry]) -> str:
    """Format a list of gshadow objects for use in /etc/shadow.

    Args:
        gshadows: list of gshadows to format

    Returns:
        string with formatted gshadow file
    """
    output = ""
    for passwd in gshadows:
        output += str(passwd) + "\n"
    return output
