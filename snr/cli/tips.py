"""
List of tips for users
"""

import random

__all__ = [
    "TIPS", "random_tip"
]

# pylint: disable=line-too-long

TIPS = [
    r"You can set output of a command to a variable using set: set !<var_name> <command>",
    r"If a variable has type of IP, IPv4 or IPv6 Address. You can pass a domain name or an interface name, for example: set LHOST tun0",
    r"You cannot delete variables defined by payloads, instead using set <var_name> or unset <var_name> will reset it to it's default value",
    r"You can define value of a variable from a file using: set !<var_name> read <file_name>",
    r"Search for payloads using list: list infection",
    r"Use misc/multi payload to bundle several payloads into one, it is powerful",
    r"Write use with no argument to unload the current payload",
    r"You can use ${<var_name>} to expand a variable as well, for example: set <var_name> ${var_name}.php",
    r"You can append data before and after strings: set <var_name> prefix${var_name}suffix. Example: set my_var ${my_var}/32",
    r"Toggle Option variables using: set <var_name> !",
    r"Just like strings, you can extend lists as well: set <var_name> data1;data2;${<var_name>};data9",
    r"Help command can be used for more than help on commands, you can get help on defined variables as well",
    r"Payloads are categorized by their usage: access, extraction, infection, misc, tampering",
    r"Access type payloads create access: Like changing admin or root password for you or opening up a ssh server",
    r"Extraction type payloads extract data: Like copying files or account password hashes",
    r"Infection type payloads infect target OS with payloads: Like installing a persistant meterpreter for you"
    r"Tampering type payloads tamper with data on disk: Like changing passwords or swapping files"
    r"Misc type payloads are the powerful misfits of Snr which offer unique payloads: Like misc/multi which allows bundling several payloads"
]


def random_tip() -> str:
    """Return a random tip

    Returns:
        Random tip from TIPS
    """
    return random.choice(TIPS)
