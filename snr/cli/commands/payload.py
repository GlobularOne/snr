"""
Payload-related commands
"""
import os
import sys

import click

from snr.cli import interactive_shell, variables
from snr.core.core import context, options
from snr.core.payload_generation import (common, generation,
                                         payload_generation_post,
                                         payload_generation_pre)
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
        generation.unload(options.payload_path, getattr(
            options.payload_module, "payload"))
        options.payload_module = None
        options.payload_path = ""
        interactive_shell.prompt = options.PROMPT_UNLOADED
        if len(payload) == 0:
            common_utils.print_info("Payload unloaded")
            return None
    cwd = os.getcwd()
    common_utils.print_debug(f"Appending '{cwd}' to sys.path")
    sys.path.append(cwd)
    payload_instance = generation.load(payload, store_cwd=True)
    sys.path.remove(cwd)
    if payload_instance is None:
        return None
    common_utils.print_info("Payload loaded")
    options.payload_module = sys.modules[payload_instance.__module__]
    options.payload_path = payload
    interactive_shell.prompt = options.PROMPT_LOADED_FORMAT.format(
        payload)
    # Add standard options
    variables.global_vars.set_variable(
        "VERBOSITY", "normal", -1, "Payload verbosity: Either quiet, normal, verbose or debug", True)
    return None


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
    if not payload_generation_pre(ctx):
        common_utils.print_error("Payload pre generation failed")
        return None
    install_snr_core.install_snr_core_lib(ctx)
    common_utils.print_debug(
        "Pre payload generation steps completed successfully")
    errorcode = generation.generate(options.payload_path, getattr(
        options.payload_module, "payload"), ctx)
    if errorcode != 0:
        common.clean_and_exit(
            ctx, f"Payload generation failed ({repr(errorcode)})")
        return None
    common_utils.print_debug(
        "Payload generated successfully. Starting post payload generation steps")
    if not payload_generation_post(ctx, verbosity):
        common_utils.print_error("Payload post generation failed")
        common.clean_on_success(ctx, True, True)
        return None
    programs.Sync().invoke_and_wait(None)
    common_utils.print_ok("Payload generation process complete")
    common_utils.print_debug(
        "Cleaning up after the payload generation process")
    common.clean_on_success(ctx, True, True)
    return None
