"""
Payload generation process
"""
import importlib
import os

from snr.core.core import options
from snr.core.payload import payload
from snr.core.util import common_utils

__all__ = (
    "load", "generate",
    "unload"
)

_orig_path: str


def load(path: str, store_cwd: bool = False) -> payload.Payload | None:
    """Load a payload

    Args:
        path: Where the payload's package is
        store_cwd (bool, optional): Whatever to override the original cwd or not. 
                                    Don't use it unless you absolutely know what you are doing.
                                    Defaults to False.

    Returns:
        Loaded payload or None if loading failed
    """
    if store_cwd:
        global _orig_path  # pylint: disable=global-statement
        _orig_path = os.getcwd()
    with common_utils.temp_chdir(_orig_path):
        orig_path = path
        common_utils.print_debug(f"Trying to load payload {orig_path}")
        path = path.replace("/", ".").replace("\\", ".")
        module = importlib.import_module(path)
        if not hasattr(module, "payload"):
            common_utils.print_error(f"{path} is not a valid payload")
            return None
        common_utils.print_debug(
            f"Calling load() function of payload {orig_path}")
        with common_utils.temp_chdir(orig_path):
            errorcode = common_utils.call_external_function(
                module.payload.load)
        if errorcode or errorcode is common_utils.EXTERNAL_CALL_FAILURE:
            common_utils.print_error(
                f"Payload {orig_path} failed to load ({errorcode})")
            del module
            return None
        if options.payload_module is None:
            options.payload_module = module
            options.payload_path = path
        return getattr(module, "payload")


def generate(name: str, p: payload.Payload, ctx: payload.Context) -> int:
    """Generate a loaded payload

    Args:
        name: Name of the payload, which is usually the relative path to the payload
        p: Payload to generate
        ctx: Context

    Returns:
        0 if successful, otherwise any other value
    """
    with common_utils.temp_chdir(_orig_path):
        common_utils.print_info(
            f"Generating payload {name}")
        with common_utils.temp_chdir(name):
            errorcode = common_utils.call_external_function(p.generate, ctx)
            if errorcode or errorcode is common_utils.EXTERNAL_CALL_FAILURE:
                common_utils.print_error(
                    f"Payload {name} failed to generate")
                return errorcode
    return 0


def unload(name: str, p: payload.Payload) -> int:
    """Unload a payload

    Args:
        name: Name of the payload, which is usually the relative path to the payload
        p: Payload to unload

    Returns:
        0 if successful, otherwise any other value. Even if an error had occurred, unload must not be called again.
    """
    common_utils.print_debug(f"Calling unload() function of payload {name}")
    return p.unload()
