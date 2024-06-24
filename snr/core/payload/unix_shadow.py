"""
Clean interface to shadow entries and a few utility functions
"""
import os.path

__all__ = (
    "PASSWORD_NO_LOGIN", "UnixShadowEntry",
    "parse_unix_shadow_line", "parse_unix_shadow_file",
    "format_unix_shadow_line", "format_unix_shadow_file"
)

# If a shadow entry's password field equals this, no password is required
PASSWORD_NO_LOGIN = "*"


class UnixShadowEntry:  # pylint: disable=too-many-instance-attributes, too-few-public-methods
    """A shadow entry

    Attributes:

        login_name: Username
        password: Hash of the password
        password_change_date: Date of password change
        min_password_age: Number of days that must pass from password_change_date for
          user to change their password
        max_password_age: Number of days after password_change_date that
          user must change their password
        password_warn_period: Number of days the user must be warned before
          their password expires
        password_inactivity_period: After password expiry, for how long the password
          must still be valid for a password change
        expiration_date: Account expiration date
        reserved: Reserved field
        locked: Whatever the user can login or not
    """
    login_name: str
    password: str
    password_change_date: str
    min_password_age: str
    max_password_age: str
    password_warn_period: str
    password_inactivity_period: str
    expiration_date: str
    reserved: str
    locked: bool

    # pylint: disable=too-many-arguments
    def __init__(self, login_name: str, password: str,
                 password_change_date: str, max_password_age: str,
                 min_password_age: str, password_warn_period: str,
                 password_inactivity_period: str, expiration_date: str,
                 reserved: str, locked: bool):
        self.login_name = login_name
        self.password = password
        self.password_change_date = password_change_date
        self.max_password_age = max_password_age
        self.min_password_age = min_password_age
        self.password_warn_period = password_warn_period
        self.password_inactivity_period = password_inactivity_period
        self.expiration_date = expiration_date
        self.reserved = reserved
        self.locked = locked

    def __str__(self) -> str:
        locked_str = "" if self.locked else "!"
        return f"{self.login_name}:{locked_str}{self.password}:" + \
            f"{self.password_change_date}:{self.max_password_age}:" + \
            f"{self.min_password_age}:{self.password_warn_period}:" + \
            f"{self.password_inactivity_period}:{self.expiration_date}:{self.reserved}"


def parse_unix_shadow_line(line: str) -> UnixShadowEntry:
    """Parse a shadow line and return a UnixShadowEntry

    Args:
        line: The line to parse.

    Returns:
        The parsed UnixShadowEntry
    """
    login_name, password, password_change_date, \
        max_password_age, min_password_age, password_warn_period, \
        password_inactivity_period, expiration_date, reserved = line.split(
            ":", 9)
    locked = False
    if password.startswith("!"):
        password = password[1:]
        locked = True
    return UnixShadowEntry(login_name, password, password_change_date,
                           max_password_age, min_password_age, password_warn_period,
                           password_inactivity_period, expiration_date,
                           reserved, locked)


def parse_unix_shadow_file(root: str = "/") -> list[UnixShadowEntry]:
    """Parse the shadow file and return list of shadow objects

    Args:
        root: Root of the directory to look for shadow file

    Returns:
        list of shadow objects
    """
    shadow_file = os.path.join(root, "etc", "shadow")
    shadows = []
    with open(shadow_file, encoding="utf-8") as stream:
        for line in stream.readlines():
            if len(line.strip()) != 0:
                shadows.append(parse_unix_shadow_line(line))
    return shadows


def format_unix_shadow_line(shadow: UnixShadowEntry) -> str:
    """Format a UnixShadowEntry for use in /etc/shadow.

    Args:
        shadow: The UnixShadowEntry to format.

    Returns:
        The formatted string representation of the UnixShadowEntry
    """
    return str(shadow)


def format_unix_shadow_file(shadows: list[UnixShadowEntry]) -> str:
    """Format a list of shadow objects for use in /etc/shadow.

    Args:
        shadows: list of shadows to format

    Returns:
        string with formatted shadow file
    """
    output = ""
    for shadow in shadows:
        output += str(shadow) + "\n"
    return output
