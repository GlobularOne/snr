"""
Clean interface to passwd entries and a few utility functions
"""
import os.path

__all__ = (
    "SHADOW_PASSWORD", "UnixPasswdEntry",
    "parse_unix_passwd_line", "parse_unix_passwd_file",
    "format_unix_passwd_line", "format_unix_passwd_file"
)

# If a passwd entry's password field equals this, the password is stored in /etc/shadow
SHADOW_PASSWORD = "x"


class UnixPasswdEntry:  # pylint: disable=too-many-instance-attributes, too-few-public-methods
    """A passwd entry

    Attributes:
        login_name: Username
        password: Password of the user
        uid: User ID of the user
        gid: Group ID of the user's primary group
        comment: A comment on the user
        home: User's home directory
        shell: User's shell
        locked: Whatever login is possible as the user or not
    """
    login_name: str
    password: str
    uid: int
    gid: int
    comment: str
    home: str
    shell: str
    locked: bool

    def __init__(self, login_name: str, password: str,  # pylint: disable=too-many-arguments
                 uid: int, gid: int, comment: str,
                 home: str, shell: str, locked: bool):
        self.login_name = login_name
        self.password = password
        self.uid = uid
        self.gid = gid
        self.comment = comment
        self.home = home
        self.shell = shell
        self.locked = locked

    def __str__(self) -> str:
        locked_str = ""
        if self.locked:
            locked_str = "!"
        return f"{self.login_name}:{locked_str}{self.password}:" + \
            f"{self.uid}:{self.gid}:{self.comment}:{self.home}:{self.shell}"

    def is_password_stored_in_shadow(self) -> bool:
        """Checks whatever password is stored in shadow file not

        Returns:
            Whatever the password is stored in a shadow file or not
        """
        return self.password == SHADOW_PASSWORD


def parse_unix_passwd_line(line: str) -> UnixPasswdEntry:
    """Parse a passwd line and return a UnixPasswdEntry

    Args:
        line: The line to parse.

    Returns:
        The parsed UnixPasswdEntry
    """
    login_name, password, uid, gid, comment, home, shell = line.split(":", 7)
    locked = False
    if password.startswith("!"):
        password = password[1:]
        locked = True
    if len(shell) == 0:
        shell = "/bin/sh"
    return UnixPasswdEntry(login_name, password, int(uid), int(gid), comment, home, shell, locked)


def parse_unix_passwd_file(root: str = "/") -> list[UnixPasswdEntry]:
    """Parse the passwd file and return list of passwd objects

    Args:
        root: Root of the directory to look for passwd file

    Returns:
        list of passwd objects
    """
    passwd_file = os.path.join(root, "etc", "passwd")
    passwds = []
    with open(passwd_file, encoding="utf-8") as stream:
        for line in stream.readlines():
            if len(line.strip()) != 0:
                passwds.append(parse_unix_passwd_line(line))
    return passwds


def format_unix_passwd_line(passwd: UnixPasswdEntry) -> str:
    """Format a UnixPasswdEntry for use in /etc/passwd

    Args:
        passwd The UnixPasswdEntry to format

    Returns:
        The formatted string representation of the UnixPasswdEntry
    """
    return str(passwd)


def format_unix_passwd_file(passwds: list[UnixPasswdEntry]) -> str:
    """Format a list of passwd objects for use in /etc/shadow.

    Args:
        passwds list of passwds to format
    Returns:
        string with formatted passwd file
    """
    output = ""
    for passwd in passwds:
        output += str(passwd) + "\n"
    return output
