"""
Clean interface to group entries and a few utility functions
"""
import copy
import os.path

__all__ = (
    "UnixGroupEntry", "parse_unix_group_line",
    "parse_unix_group_file", "format_unix_group_line",
    "format_unix_group_file"
)


class UnixGroupEntry:  # pylint: disable=too-few-public-methods
    """A group entry

    Attributes:
        group_name: Name of the group
        password: Password of the group
        gid: ID of the group
        user_list: List of users in the group
    """
    group_name: str
    password: str
    gid: int
    user_list: list[str]

    def __init__(self, group_name: str, password: str,
                 gid: int, user_list: list[str]):
        self.group_name = group_name
        self.password = password
        self.gid = gid
        self.user_list = copy.deepcopy(user_list)

    def __str__(self) -> str:
        return f"{self.group_name}:{self.password}:{self.gid}:{','.join(self.user_list)}"


def parse_unix_group_line(line: str) -> UnixGroupEntry:
    """Parse a group line and return a UnixGroupEntry

    Args:
        line The line to parse.

    Returns:
        The parsed UnixGroupEntry
    """
    group_name, password, gid, user_list_raw = line.split(":", 4)
    user_list = user_list_raw.split(",")
    return UnixGroupEntry(group_name, password, int(gid), user_list)


def parse_unix_group_file(root: str = "/") -> list[UnixGroupEntry]:
    """Parse the group file and return list of group objects

    Args:
        root: root of the directory to look for group file

    Returns:
        list of group objects
    """
    group_file = os.path.join(root, "etc", "group")
    groups = []
    with open(group_file, encoding="utf-8") as stream:
        for line in stream.readlines():
            if len(line.strip()) != 0:
                groups.append(parse_unix_group_line(line))
    return groups


def format_unix_group_line(group: UnixGroupEntry) -> str:
    """Format a UnixGroupEntry for use in /etc/group.

    Args:
        group The UnixGroupEntry to format.

    Returns:
        The formatted string representation of the UnixGroupEntry
    """
    return str(group)


def format_unix_group_file(groups: list[UnixGroupEntry]) -> str:
    """Format a list of group objects for use in /etc/shadow.

    Args:
        groups: list of groups to format

    Returns:
        string with formatted group file
    """
    output = ""
    for group in groups:
        output += str(group) + "\n"
    return output
