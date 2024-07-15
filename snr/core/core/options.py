"""
User-passed options and shared variables
"""
import configparser
import os.path
import socket
import types
from typing import Mapping, Optional, TypedDict

from snr.core.core import common_paths

__all__ = (
    "debug", "verbose",
    "quiet", "initializing",
    "default_exit_code", "arch",
    "PROMPT_UNLOADED", "PROMPT_LOADED_FORMAT",
    "payload_path", "payload_module",
    "MINIMUM_TARGET_SIZE", "default_hostname",
    "default_primary_nameserver", "default_secondary_nameserver",
    "default_user_agent"
)

_ValidConfigValueType = type[str | int | bool]


class _TypeSchemaDictRequired(TypedDict):
    type: _ValidConfigValueType


class _TypeSchemaDict(_TypeSchemaDictRequired, TypedDict, total=False):
    alphanum_only: Optional[bool]
    ipaddress_only: Optional[bool]


_CONFIG_SCHEMA: Mapping[str, _TypeSchemaDict] = {
    "debug": {
        "type": bool,
    },
    "verbose": {
        "type": bool,
    },
    "quiet": {
        "type": bool,
    },
    "arch": {
        "type": str,
    },
    "default_exit_code": {
        "type": int,
    },
    "default_hostname": {
        "type": str,
        "alphanum_only": True
    },
    "default_primary_nameserver": {
        "type": str,
        "ipaddress_only": True
    },
    "default_secondary_nameserver": {
        "type": str,
        "ipaddress_only": True
    },
    "default_user_agent": {
        "type": str
    }
}

# Whatever snr is run in verbose mode or not
verbose: bool = False

# Whatever or not snr is run in quiet mode
quiet: bool = False

# Whatever or not snr is initializing
initializing: bool = False

# Snr's default exit code
default_exit_code: int = 0

# System architecture
arch: str

# Prompt when no payload is loaded
PROMPT_UNLOADED = "snr> "

# Format for the prompt when a payload is loaded
PROMPT_LOADED_FORMAT = "snr ({0})> "

# Path to the currently loaded payload
payload_path: str = ""

# Python module of the loaded payload or None if no payload is loaded
payload_module: types.ModuleType | None = None

# Minimum size all target mediums must at least be
MINIMUM_TARGET_SIZE = 2000 * 1024 * 1024

# Default hostname of generated images
default_hostname: str = "snr"

# Default primary dns of generated images
default_primary_nameserver: str = "1.1.1.1"

# Default secondary dns of generated images
default_secondary_nameserver: str = "1.0.0.1"

# Default user agent
default_user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0"

# If catching an exception, drop to a debug shell
debug: bool = False


def _validate_and_apply_str(option: str, value: str) -> None:
    if _CONFIG_SCHEMA[option].get("alphanum_only", False):
        if not value.isalnum():
            print(f"--> Configuration value of '{option}'"
                  "is not a valid alphanumeric string")
            return
        if _CONFIG_SCHEMA[option].get("ipaddress_only", False):
            try:
                socket.inet_pton(socket.AF_INET, value)
            except OSError:
                print(f"--> Configuration value of '{option}'"
                      "is not a valid ip address")
                return
    globals()[option] = value


def _validate_and_apply_int(option: str, value: str) -> None:
    try:
        int(value, base=10)
    except ValueError:
        print(f"--> Configuration value of '{option}' is not a valid integer")
        return
    globals()[option] = int(value, base=10)


def _validate_and_apply_bool(option: str, value: str) -> None:
    if value.lower() in ("y", "on", "yes"):
        globals()[option] = True
    elif value.lower() in ("n", "off", "no"):
        globals()[option] = False
    else:
        print(f"--> Configuration value of '{option}' is not a valid boolean")


def _validate_and_apply_config(config_parser: configparser.ConfigParser) -> None:
    global verbose  # pylint: disable=global-statement
    global quiet  # pylint: disable=global-statement
    for option, value in config_parser.items("main"):
        if option not in _CONFIG_SCHEMA:
            print(f"--> Configuration key '{option}' is not recognized")
            continue
        if _CONFIG_SCHEMA[option]["type"] is bool:
            _validate_and_apply_bool(option, value)
        if _CONFIG_SCHEMA[option]["type"] is int:
            _validate_and_apply_int(option, value)
        if _CONFIG_SCHEMA[option]["type"] is str:
            _validate_and_apply_str(option, value)
        # Just like on command line, passing both cancel each other out
        if quiet and verbose:
            print("--> Configuration specifies both quiet and verbose as true,"
                  "they will cancel each other out")
            quiet, verbose = False, False


def _parse_config() -> None:
    if not hasattr(_parse_config, "has_already_done"):
        config_parser = configparser.ConfigParser()
        config_parser.read_dict(
            {
                "main": {
                    "verbose": verbose,
                    "quiet": quiet,
                    "default_exit_code": default_exit_code,
                    "default_hostname": default_hostname,
                    "default_primary_nameserver": default_primary_nameserver,
                    "default_secondary_nameserver": default_secondary_nameserver,
                    "default_user_agent": default_user_agent
                }
            }
        )
        config_parser.read(os.path.join(
            common_paths.CONFIG_PATH, "main.conf"))
        _validate_and_apply_config(config_parser)
