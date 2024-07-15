"""
Module containing a class providing a more clean interface to work with systemd unit files
"""
import configparser
import os
import pprint
import warnings

from snr.core.core import context
from snr.core.util import common_utils

__all__ = (
    "SYSTEMD_SYSTEM_PATH", "SystemdConfigFileBase",
    "SystemdUnit"
)


def SYSTEMD_SYSTEM_PATH(ctx: context.Context) -> str:  # pylint: disable=invalid-name
    """Return the path to systemd's system directory
    
    Args:
        ctx: A dictionary containing context information
    
    Returns:
        The path to systemd's system directory
    """
    return ctx.join("usr", "lib", "systemd", "system")


_ValidOptionValueType = str | int | bool
# Type for a system section
SystemdSectionType = dict[str, _ValidOptionValueType]


class _SystemdConfigParser(configparser.ConfigParser):
    def optionxform(self, optionstr: str) -> str:
        return optionstr


class SystemdConfigFileBase:
    """Provide basic systemd unit file parsing, is not usually used directly.
    """
    _base_sections: tuple[str, ...] = ()
    _extra_sections: tuple[str, ...] = ()
    root: str = ""
    path: str = ""
    suffix: str = ""
    basename: str = ""

    def __init_subclass__(cls, root: str, base_sections: tuple[str, ...] = ()) -> None:
        cls.root = root
        cls._base_sections = tuple(base_sections)

    def read(self) -> None:
        """Read and parse configuration file

        Raises:
            FileNotFoundError: If the config file does not exist
        """
        parser = _SystemdConfigParser()
        if len(parser.read(self.path)) != 1:
            raise FileNotFoundError(
                f"No such file or directory: {self.path}")
        section_names = parser.sections()
        for section_name in section_names:
            section_name = section_name.replace("-", "_")
            if section_name in self._extra_sections or section_name in self._base_sections:
                setattr(self, f"{section_name}_section",
                        {**parser[section_name]})
            else:
                warnings.warn(
                    f"SystemdUnit: Unrecognized section '{section_name}'")

    def _write(self) -> None:
        """Write the unit file
        """
        sections = {}
        for section_name in self._base_sections:
            sections[section_name.replace(
                "_", "-")] = getattr(self, f"{section_name}_section")
        for section_name in self._extra_sections:
            sections[section_name.replace(
                "_", "-")] = getattr(self, f"{section_name}_section")
        common_utils.print_debug(
            f"Writing unit file {self.basename} with data:\n{pprint.pformat(sections)}")
        parser = _SystemdConfigParser()
        parser.read_dict(sections)
        with open(self.path, "w", encoding="utf-8") as stream:
            parser.write(stream, False)

    def write(self) -> None:
        """Write unit the file
        """
        self._write()


class SystemdUnit(SystemdConfigFileBase,
                  root="/nonexistent",
                  base_sections=("Unit", "Install")):
    """Provide a more clean interface to work with systemd unit files
    """
    Unit_section: SystemdSectionType = {}
    Install_section: SystemdSectionType = {}
    _context: context.Context

    def __init__(self, ctx: context.Context, name: str):
        for extra_section in self._extra_sections:
            setattr(self, f"{extra_section}_section", {})
        for base_section in self._base_sections:
            setattr(self, f"{base_section}_section", {})
        self.root = SYSTEMD_SYSTEM_PATH(ctx)
        self.path = os.path.join(self.root, name + self.suffix)
        self.basename = os.path.basename(self.path)
        self._context = ctx

    def __init_subclass__(cls, suffix: str, extra_sections: tuple[str, ...] = ()):
        cls.suffix = suffix
        cls._extra_sections = tuple(extra_sections)

    def write(self, make_wants_dir: bool = True, make_requires_dir: bool = True) -> None:
        """Write the config to disk
        
        Args:
            make_wants_dir: Whether or not to make the .wants directory.
            make_requires_dir: Whether or not to make the .requires directory
        """
        self._write()
        if make_wants_dir:
            os.mkdir(os.path.join(self.root, self.basename) + ".wants")
        if make_requires_dir:
            os.mkdir(os.path.join(self.root, self.basename) + ".requires")
