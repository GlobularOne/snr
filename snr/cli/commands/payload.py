"""
Payload-related commands
"""
import importlib
import os
import sys

import click

from snr.cli import interactive_shell, variables
from snr.core.core import context, options
from snr.core.payload import safety_pin
from snr.core.payload_generation import common
from snr.core.payload_generation.post import (core_configuration, finishing,
                                              grub_installation)
from snr.core.payload_generation.pre import (ensuring_dependencies, formatting,
                                             host_check, partitioning,
                                             rootfs_preparation)
from snr.core.util import common_utils, programs
from snr.core.util.payloads import install_snr_core


@interactive_shell.interactive_shell.command(name="use")
@click.argument("payload", type=click.Path(exists=True, file_okay=False), required=False)
def cmd_use(payload: str) -> str | None:
    """\
Use a payload
    """
    if options.payload_module is not None or \
            (payload is None and options.payload_module is not None):
        common_utils.print_debug("Calling unload() function of payload")
        common_utils.call_external_function(
            getattr(options.payload_module.payload, "unload"))  # pylint: disable=no-member
        options.payload_module = None
        options.payload_path = ""
        interactive_shell.prompt = options.PROMPT_UNLOADED
        if payload is None:
            common_utils.print_info("Payload unloaded")
            return None
    cwd = os.getcwd()
    path = payload.replace("/", ".").replace("\\", ".")
    common_utils.print_debug(f"Appending '{cwd}' to sys.path")
    sys.path.append(cwd)
    common_utils.print_debug("Importing payload")
    module = importlib.import_module(path)
    if not hasattr(module, "payload"):
        common_utils.print_error("Not a valid payload")
        return None
    common_utils.print_debug("Calling load() function of payload")
    errorcode = common_utils.call_external_function(module.payload.load)
    if errorcode or errorcode is common_utils.EXTERNAL_CALL_FAILURE:
        common_utils.print_error(f"Payload failed to load ({errorcode})")
        del module
        return None
    sys.path.remove(cwd)
    common_utils.print_info("Payload loaded")
    options.payload_module = module
    options.payload_path = payload
    interactive_shell.prompt = options.PROMPT_LOADED_FORMAT.format(
        payload)
    # Add standard options
    variables.global_vars.set_variable(
        "VERBOSITY", "normal", -1, "Payload verbosity: Either quiet, normal, verbose or debug", True)
    return None


def _payload_generate_pre(ctx: context.Context) -> bool:
    if not host_check.check_host(ctx):
        return False
    if not partitioning.partition_host(ctx):
        return False
    if not formatting.format_host(ctx):
        return False
    if not rootfs_preparation.prepare_rootfs(ctx):
        return False
    if not ensuring_dependencies.ensure_dependencies(ctx):
        return False
    return True


def _payload_generate_post(ctx: context.Context, verbosity: str) -> bool:
    safety_pin.remove_safety_pin(ctx.root_directory)
    if not core_configuration.configure_core(ctx, verbosity):
        return False
    if not grub_installation.install_grub(ctx):
        return False
    if not finishing.finish_host(ctx):
        return False
    return True


@interactive_shell.interactive_shell.command(name="generate")
@click.argument("device", type=click.Path(exists=True, dir_okay=False, writable=True), required=True)
def cmd_generate(device: str) -> str | None:
    """\
Generate a selected payload, pass device to write to as an argument
    """
    if options.payload_module is None:
        common_utils.print_error("No payload selected")
        return None
    verbosity = variables.global_vars.get_variable_str("VERBOSITY").lower()
    if verbosity not in ("quiet", "normal", "verbose", "debug"):
        common_utils.print_error(f"Unknown verbosity '{verbosity}'")
        return None
    common_utils.print_debug("Starting payload generation process")
    ctx = context.Context(device)
    common_utils.print_info("Generating payload")
    common_utils.print_debug("Starting pre payload generation process")
    if not _payload_generate_pre(ctx):
        common_utils.print_error("Payload pre generation failed")
        return None
    install_snr_core.install_snr_core_lib(ctx)
    common_utils.print_debug(
        "Pre payload generation steps completed successfully")
    common_utils.print_debug("Calling generate() method of payload")
    errorcode = getattr(getattr(options.payload_module,
                        "payload"), "generate")(ctx)
    if errorcode != 0:
        common.clean_and_exit(
            ctx, f"Payload generation failed ({repr(errorcode)})")
        return None
    common_utils.print_debug(
        "Payload generated successfully. Starting post payload generation steps")
    if not _payload_generate_post(ctx, verbosity):
        common_utils.print_error("Payload post generation failed")
        common.clean_on_success(ctx, True, True)
        return None
    programs.Sync().invoke_and_wait(None)
    common_utils.print_ok("Payload generation process complete")
    common_utils.print_debug(
        "Cleaning up after the payload generation process")
    common.clean_on_success(ctx, True, True)
    return None
