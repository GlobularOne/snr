"""
Filesystem-related commands
"""
import hashlib as _hashlib
import os as _os

from libsnr.core import common_paths as _common_paths
from libsnr.util.common_utils import print_debug as _print_debug
from libsnr.util.common_utils import print_error as _print_error


def cmd_pwd(_, __):
    """\
Print current working directory
    """
    return _os.getcwd()


def cmd_chdir(argv, argc):
    """\
Change current working directory
    """
    if argc == 0:
        args = _common_paths.CACHE_PATH
    else:
        args = " ".join(argv)
    try:
        _os.chdir(args)
        _print_debug(f"New working directory: '{args}'")
    except FileNotFoundError as exc:
        _print_error("No such file or directory")
        _print_debug(exc)


def cmd_list(argv, argc):
    """\
List files and directory inside a directory\
 or current working directory if none passed
    """
    if argc == 0:
        args = _os.getcwd()
    else:
        args = " ".join(argv)
    output = ""
    for entry in _os.listdir(args):
        if _os.path.isdir(entry):
            output += f"{entry}/\n"
        else:
            output += f"{entry}\n"
    return output


def cmd_read(argv, argc):
    """\
Read the content of a file
    """
    if argc == 0:
        _print_error("read requires an argument")
        return None
    args = " ".join(argv)
    if _os.path.isdir(args):
        _print_error(f"{args} is a directory")
        return None
    try:
        with open(args, "r", encoding="utf-8") as file:
            content = file.read()
    except Exception as exc:  # pylint: disable=broad-exception-caught
        _print_error(f"Could not read file '{args}'")
        _print_error(exc)
        return None
    return content


def cmd_checksum(argv, argc):
    """\
Calculate checksum of a file.
Valid algorithms are: blake2b, md5, sha1, sha224, sha256, sha384, sha512
    """
    valid_algorithms = ["blake2b", "md5", "sha1",
                        "sha224", "sha256", "sha384", "sha512"]
    if argc < 2:
        _print_error("checksum <algorithm> <file>")
        return None
    algorithm, file = argv[0], " ".join(argv[1:])
    if algorithm not in valid_algorithms:
        _print_error(f"Invalid algorithm '{algorithm}'"
                     f"(Valid algorithms: {' '.join(valid_algorithms)})")
        return None
    if not _os.path.exists(file):
        _print_error("No such file or directory")
        return None
    if _os.path.isdir(file):
        _print_error(f"{file} is a directory")
        return None
    try:
        with open(file, "rb") as file:
            return _hashlib.file_digest(file, algorithm).hexdigest()
    except Exception as exc:  # pylint: disable=broad-exception-caught
        _print_error("Could not generate checksum")
        _print_debug(exc)
    return None
