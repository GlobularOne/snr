"""
Wrap a program
"""
import os
import shlex
import shutil
import subprocess
from subprocess import DEVNULL, PIPE, STDOUT, SubprocessError
from typing import IO, Mapping

from snr.core.util import common_utils

__all__ = (
    "DEVNULL", "PIPE",
    "STDOUT", "SubprocessError",
    "ProgramWrapperBase", "program_wrapper_factory",
)


class ProgramWrapperBase:  # pylint: disable=too-many-instance-attributes
    """Wrap a program

    Do note that you must absolutely not use this class directly but use it's factory

    Attributes:
        _path: Path of the program to execute
        cwd: Working directory of the program
        command_verb: Command verb of the program (the first option passed on the command line,
          comes before args and options)
        args: Arguments to pass on the command line
        options: Options to pass on the command line
        sudo: Whatever the command should be run with sudo or not
        fakeroot: Whatever the command should be run with fakeroot or not
        fakechroot: Whatever the command should be run with fakechroot or not
        stdin: Executed program's stdin
        stdout: Executed program's stdout
        stderr: Executed program's stderr
    """
    cwd: None | str
    command_verb: None | str
    args: list[str]
    options: dict[str, str | None]
    sudo: bool
    fakeroot: bool
    fakechroot: bool
    stdin: IO[str] | None = None
    stdout: IO[str] | None = None
    stderr: IO[str] | None = None

    # These are private, we don't expect the user to manipulate these
    _path: str | None
    _interpreter: tuple[str, str] = ("", "")
    _process: None | subprocess.Popen[str]
    _stdin: int | None = None
    _stdout: int | None = None
    _stderr: int | None = None

    def __init__(self,
                 *args: str, stdin: int | None = None,
                 stdout: int | None = None, stderr: int | None = None,
                 command_verb: None | str = None,
                 options: dict[str, str] | None = None,
                 cwd: None | str = None, sudo: bool = False,
                 fakeroot: bool = False, fakechroot: bool = False):
        self.command_verb = command_verb
        self.args = [*args]
        if options is None:
            self.options = {}
        else:
            self.options = {**options}
        self.cwd = cwd
        self.sudo = sudo
        self.fakeroot = fakeroot
        self.fakechroot = fakechroot

        if sudo and (self.fakechroot or self.fakeroot):
            raise ValueError("Fakechroot or fakeroot cannot be used with sudo")

        self._process = None
        self._stdin = stdin
        self._stdout = stdout
        self._stderr = stderr

    def __init_subclass__(cls, program: str | None = None, interpreter: tuple[str, str] = ("", "")):
        cls._path = program
        cls._interpreter = interpreter

    def __repr__(self) -> str:
        return f"{type(self).__name__}("\
            f"{repr(self._path)}, {repr(self.args)}, "\
            f"command_verb={repr(self.command_verb)}, "\
            f"options={repr(self.options)}, cwd={repr(self.cwd)})"

    def set_command_verb(self, verb: str) -> None:
        """Set the verb that will be used for command

        Args:
            verb: verb to be used for
        """
        self.command_verb = verb

    def add_arguments(self, *args: str, options: Mapping[str, str | None] | None = None) -> None:
        """Add arguments to the command

        Args:
            options: Command line options to add
        """
        self.args.extend(args)
        if options is not None:
            self.options = {**self.options, **options}

    def invoke(self, *args: str, options: Mapping[str, str | None] | None = None) -> None:
        """Invoke the program with the given arguments

        Raises:
            TypeError: If the class was used directly and not a factory was used
        Args:
            options: Command line options to add
        """
        if not self._interpreter[0].endswith("chroot"):
            # Only search for it when we are going to execute it ourselves
            # When using chroot, just pass the command as it is
            if self._path is not None:
                if not os.path.isabs(self._path):
                    path = shutil.which(self._path)
                    if path is None:
                        raise FileNotFoundError(
                            f"Could not find program: '{self._path}'")
                    self._path = path
        if self._path is None:
            raise TypeError(
                "ProgramWrapperBase used directly, use one of it's factories")
        # First ensure the program isn't already running
        if self._process is not None:
            if self._process.returncode is None:
                # Program is still running
                raise SubprocessError(
                    f"Program '{self._path}' is already running")
        self._process = None
        env = os.environ
        cwd = os.getcwd() if self.cwd is None else self.cwd
        self.add_arguments(*args, options=options)
        cmdline: list[str] = []
        if self.sudo and os.getuid() != 0:
            sudo_path = shutil.which("sudo")
            if sudo_path is None:
                raise SubprocessError(
                    "Usage of sudo requested yet sudo is not found on PATH")
            cmdline.append(sudo_path)
        if self.fakechroot and os.getuid() != 0:
            fakechroot_path = shutil.which("fakechroot")
            if fakechroot_path is None:
                raise SubprocessError(
                    "Usage of fakechroot requested yet fakechroot is not found on PATH")
            env["FAKECHROOT_EXCLUDE_PATH"] = ""
            cmdline.append(fakechroot_path)
        if self.fakeroot and os.getuid() != 0:
            fakeroot_path = shutil.which("fakeroot")
            if fakeroot_path is None:
                raise SubprocessError(
                    "Usage of fakeroot requested yet fakeroot is not found on PATH")
            cmdline.append(fakeroot_path)
        if self._interpreter is None or self._interpreter[0] != "":
            cmdline.extend(self._interpreter)
        cmdline.append(self._path)
        if self.command_verb is not None:
            cmdline.append(shlex.quote(self.command_verb))
        for option, value in self.options.items():
            if len(option) == 1:
                cmdline.append("-" + option)
            else:
                cmdline.append("--" + option)
            if value is not None:
                cmdline.append(shlex.quote(value))
        cmdline.extend([shlex.quote(arg) for arg in self.args])
        common_utils.print_debug(
            f"Executing program '{cmdline[0]}' with arguments: {cmdline[1:]}")
        self._process = subprocess.Popen(cmdline, cwd=cwd, stdin=self._stdin,  # pylint: disable=consider-using-with
                                         stdout=self._stdout, stderr=self._stderr,
                                         text=True, env=env)
        self.stdin = self._process.stdin
        self.stdout = self._process.stdout
        self.stderr = self._process.stderr

    def wait(self, timeout: float | None = None) -> int:
        """Wait for the process to exit.

        Args:
            timeout: Time in seconds to wait for the process to exit.

        Returns:
            The exit code of the process
        """
        if self._process is None:
            raise subprocess.SubprocessError("Program has never run")
        return self._process.wait(timeout)

    def invoke_and_wait(self, timeout: float | None, *args: str,
                        options: Mapping[str, str | None] | None = None) -> int:
        """Invoke and wait for result.

        Args:
            timeout: Timeout in seconds. If None wait forever.
            options: Options to pass to invoke.

        Returns:
            Exit code of the program
        """
        self.invoke(*args, options=options)
        return self.wait(timeout)


def program_wrapper_factory(program_name: str) -> type[ProgramWrapperBase]:
    """Factory function for ProgramWrapperBase

    Args:
        program_name: Name of the program to wrap

    Returns:
        A  ProgramWrapper instance wrapping the passed program
    """
    class CustomProgramWrapper(ProgramWrapperBase, program=program_name):
        """Wrap {0}"""
    class_name = program_name.title()
    class_name = class_name.replace("-", "").replace("_", "")
    CustomProgramWrapper.__name__ = class_name
    assert CustomProgramWrapper.__doc__ is not None
    CustomProgramWrapper.__doc__ = CustomProgramWrapper.__doc__.format(
        program_name)
    return CustomProgramWrapper
