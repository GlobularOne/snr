"""
Payload-related commands
"""
import importlib as _importlib
import os as _os
import sys as _sys

from libsnr.core import options as _options
from libsnr.payload_generation import (finishing, formatting,
                                       grub_installation, partitioning,
                                       satisfy_dependencies, rootfs_preparation, target_check)
from libsnr.payload_generation.common import \
    bind_required_rootfs_dirs as _bind_required_rootfs_dirs
from libsnr.payload_generation.common import clean_and_exit as _clean_and_exit
from libsnr.payload_generation.common import \
    clean_on_success as _clean_on_success
from libsnr.payload_generation.common import \
    unbind_required_rootfs_dirs as _unbind_required_rootfs_dirs
from libsnr.util.common_utils import \
    call_external_function as _call_external_function, EXTERNAL_CALL_FAILURE as _EXTERNAL_CALL_FAILURE
from libsnr.util.common_utils import print_debug as _print_debug
from libsnr.util.common_utils import print_error as _print_error
from libsnr.util.common_utils import print_info as _print_info
from libsnr.util.common_utils import print_ok as _print_ok
from libsnr.util.program_wrapper import ProgramWrapper as _ProgramWrapper
from libsnr.util.payloads.libsnr import install_libsnr as _install_libsnr
from libsnr.payload.safety_pin import remove_safety_pin as _remove_safety_pin


def cmd_use(argv, argc):
    """\
Use a payload
    """
    if _options.payload_module is not None or argc == 0:
        if hasattr(_options.payload_module, "unload") and \
                callable(getattr(_options.payload_module, "unload")):
            _print_debug("Calling unload() function of payload")
            _call_external_function(getattr(_options.payload_module, "unload"))
        _options.payload_module = None
        _options.payload_path = ""
        _options.prompt = _options.PROMPT_UNLOADED
        if argc == 0:
            _print_info("Payload unloaded")
            return
    cwd = _os.getcwd()
    args = " ".join(argv)
    path = args.replace("/", ".").replace("\\", ".")
    _print_debug(f"Appending '{cwd}' to sys.path")
    _sys.path.append(cwd)
    _print_debug("Importing payload")
    module = _importlib.import_module(path)
    if not hasattr(module, "generate"):
        _print_error("Not a valid payload")
        return
    if hasattr(module, "load"):
        _print_debug("Calling load() function of payload")
        errorcode = _call_external_function(module.load)
        if errorcode or errorcode is _EXTERNAL_CALL_FAILURE:
            _print_error(f"Payload failed to load ({errorcode})")
            del module
            return
    else:
        _print_debug("Payload has no load() function")
    _sys.path.remove(cwd)
    _print_info("Payload loaded")
    _options.payload_module = module
    _options.payload_path = args
    _options.prompt = _options.PROMPT_LOADED_FORMAT.format(args)


def cmd_generate(argv, argc):
    """\
Generate a selected payload, pass device to write to as an argument
    """
    if argc == 0:
        _print_error("generate requires an argument")
        return
    if _options.payload_module is None:
        _print_error("No payload selected")
        return
    args = " ".join(argv)
    if not _os.access(args, _os.W_OK):
        _print_error(f"'{args}' is not writable")
        return
    _print_debug("Starting payload generation process")
    context = {
        "target": args
    }
    try:
        if not target_check.check_target(context):
            return
        if not partitioning.partition_target(context):
            return
        if not formatting.format_target(context):
            return
        if not rootfs_preparation.prepare_rootfs(context):
            return
        if not satisfy_dependencies.satisfy_dependencies(context):
            return
        _print_info("Generating payload")
        _install_libsnr(context)
        _bind_required_rootfs_dirs(context)
        errorcode = _call_external_function(
            getattr(_options.payload_module, "generate"), context)
        _unbind_required_rootfs_dirs(context)
        if errorcode != 0:
            _clean_and_exit(
                context, f"Payload generation failed ({repr(errorcode)})")
            return
        _remove_safety_pin(context["temp_dir"])
        if not grub_installation.install_grub(context):
            return
        if not finishing.finish_target(context):
            return
        _ProgramWrapper("sync").invoke_and_wait(None)
        _print_ok("Payload generated successfully")
    finally:
        _clean_on_success(context, True, True)
