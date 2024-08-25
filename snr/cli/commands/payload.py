"""
Payload-related commands
"""
import os
import sys

import click
import rich.progress

from snr.cli import interactive_shell, variables
from snr.core.core import console, context, options
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
        "VERBOSITY", "normal", -1, "Payload verbosity: Either quiet, normal, verbose or debug", variables.REQUIRED)
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
    # Get sudo to cache it's access to us before we get to the progress bar
    common_utils.print_info("Getting sudo permissions")
    try:
        errorcode = programs.program_wrapper_factory(
            "true")(sudo=True).invoke_and_wait(None)
        if errorcode:
            common_utils.print_error("Sudo permissions are required")
            return None
    except KeyboardInterrupt:
        common_utils.print_error("Sudo permissions are required")
        return None
    with rich.progress.Progress(rich.progress.TextColumn("[progress.description]{task.description}"),
                                rich.progress.BarColumn(),
                                rich.progress.TaskProgressColumn(), transient=True, expand=True) as progress_field:
        orig_console = console.console
        orig_err_console = console.err_console
        console.console = progress_field.console
        console.err_console = progress_field.console
        try:
            pre_steps = payload_generation_pre(ctx)
            pre_steps_count = next(pre_steps)
            pre_steps_task = progress_field.add_task(
                "Preparing for payload generation", total=pre_steps_count + 1)
            try:
                for _ in range(pre_steps_count+1):
                    next(pre_steps)
                    progress_field.update(pre_steps_task, advance=1)
            except StopIteration as exc:
                status = exc.value
                if not status:
                    common_utils.print_error("Payload pre generation failed")
                    return None
            install_snr_core.install_snr_core_lib(ctx)
            progress_field.update(pre_steps_task, advance=1)
            common_utils.print_debug(
                "Pre payload generation steps completed successfully")
            generation_steps_task = progress_field.add_task(
                "Generating payload", total=pre_steps_count + 1)
            errorcode = generation.generate(options.payload_path, getattr(
                options.payload_module, "payload"), ctx)
            if errorcode != 0:
                common.clean_and_exit(
                    ctx, f"Payload generation failed ({repr(errorcode)})")
                return None
            progress_field.update(generation_steps_task, advance=1)
            common_utils.print_debug(
                "Payload generated successfully. Starting post payload generation steps")
            post_steps = payload_generation_post(ctx, verbosity)
            post_steps_count = next(post_steps)
            post_steps_task = progress_field.add_task(
                "Finishing payload generation", total=pre_steps_count + 1)
            try:
                for _ in range(post_steps_count+1):
                    next(pre_steps)
                    progress_field.update(post_steps_task, advance=1)
            except StopIteration as exc:
                status = exc.value
                if not status:
                    common_utils.print_error("Payload pre generation failed")
                    return None
            programs.Sync().invoke_and_wait(None)
            progress_field.update(post_steps_task, advance=1)
        finally:
            console.console = orig_console
            console.err_console = orig_err_console
    common_utils.print_ok("Payload generation process complete")
    common_utils.print_debug(
        "Cleaning up after the payload generation process")
    common.clean_on_success(ctx, True, True)
    return None
