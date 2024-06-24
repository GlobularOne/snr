"""
Filesystem-related commands
"""
import hashlib
import os
import os.path

import click

from snr.cli import interactive_shell
from snr.core.core import common_paths
from snr.core.util import common_utils


@interactive_shell.interactive_shell.command(name="pwd")
def cmd_pwd() -> str | None:
    """\
Print current working directory
    """
    return os.getcwd()


@interactive_shell.interactive_shell.command(name="chdir")
@click.argument("directory", type=click.Path(exists=True, file_okay=False), required=True)
def cmd_chdir(directory: str) -> None:
    """\
Change current working directory
    """
    if len(directory) == 0:
        directory = common_paths.CACHE_PATH
    os.chdir(directory)
    common_utils.print_debug(f"New working directory: '{directory}'")


@interactive_shell.interactive_shell.command(name="list")
@click.argument("directory", type=click.Path(exists=True, file_okay=False), required=False)
def cmd_list(directory: str | None) -> str | None:
    """\
List files and directory inside a directory\
 or current working directory if none passed
    """
    if directory is None:
        directory = os.getcwd()
    output = ""
    for entry in os.listdir(directory):
        if os.path.isdir(entry):
            output += f"{entry}/\n"
        else:
            output += f"{entry}\n"
    return output


@interactive_shell.interactive_shell.command(name="read")
@click.argument("file", type=click.Path(exists=True, dir_okay=False), required=True)
def cmd_read(file: str) -> str | None:
    """\
Read the content of a file
    """
    if os.path.isdir(file):
        common_utils.print_error(f"'{file}' is a directory")
        return None
    try:
        with open(file, "r", encoding="utf-8") as stream:
            content = stream.read()
    except OSError as exc:
        common_utils.print_error(f"Could not read file '{file}'")
        common_utils.print_error(exc)
        return None
    return content


@interactive_shell.interactive_shell.command(name="checksum")
@click.argument("algorithm", required=True,
                type=click.Choice(["blake2b", "md5", "sha1",
                                   "sha224", "sha256", "sha384", "sha512"], False))
@click.argument("file", type=click.Path(exists=True, dir_okay=False), required=True)
def cmd_checksum(file: str, algorithm: str) -> str | None:
    """\
Calculate checksum of a file.
Valid algorithms are: blake2b, md5, sha1, sha224, sha256, sha384, sha512
    """
    # Writing checksum algorithm's names as uppercase (MD5)
    # is far too common to not support
    algorithm = algorithm.lower()
    if not os.path.exists(file):
        common_utils.print_error("No such file or directory")
        return None
    if os.path.isdir(file):
        common_utils.print_error(f"{file} is a directory")
        return None
    try:
        with open(file, "rb") as stream:
            return hashlib.new(algorithm, stream.read()).hexdigest()
    except OSError as exc:
        common_utils.print_error("Could not generate checksum")
        common_utils.print_debug(exc)
    return None
