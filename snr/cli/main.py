"""
Main function, the glue code of snr
"""
import bdb
import os
import pathlib
import sys
from typing import Any

import click
import pkg_resources
import rich.traceback

from snr import version
from snr.cli import atexit_callbacks, init, interactive_shell
from snr.core.core import arch, common_paths, console, options
from snr.core.util import common_utils

__all__ = (
    "main",
)


def _check_for_libsnr() -> None:
    try:
        pkg_resources.get_distribution("libsnr")
        common_utils.print_sys(
            "The now obsolete libsnr found! It is no longer supported neither is used, remove it")
    except pkg_resources.DistributionNotFound:
        pass


def _show_version(show_version: bool) -> None:
    if show_version:
        print(
            f"snr {version.__version__}",
            f"python/{sys.version.split()[0]}",
            f"click/{pkg_resources.get_distribution('click').version}",
            f"rich/{pkg_resources.get_distribution('rich').version}",
            f"pyfiglet/{pkg_resources.get_distribution('pyfiglet').version}",
            f"prompt_toolkit/{pkg_resources.get_distribution('prompt_toolkit').version}")
        sys.exit(0)


def _handle_init(do_init: bool, do_reinit: bool, init_only: bool, init_if_needed: bool) -> None:
    common_paths.format_rootfs_archive_path(arch.get_arch())
    should_initialize = False
    # Check the made by value
    if do_reinit:
        if do_init:
            # Just issue a warning that this combination
            # doesn't sound very valid
            common_utils.print_warning("--init and --reinit used together")
        common_utils.print_warning(
            "--reinit has been deprecated. Use --init-if-needed instead")
        should_initialize = True
    elif not os.path.exists(common_paths.ROOTFS_ARCHIVE_PATH):
        # Are we allowed to initialize
        if do_init or init_if_needed:
            should_initialize = True
        else:
            common_utils.print_fatal(
                "Please re-run snr with --init to initialize")
    rootfs_version = common_utils.get_rootfs_version()
    if rootfs_version != common_paths.ROOTFS_CURRENT_VERSION and init_if_needed:
        should_initialize = True
    if not should_initialize:
        if rootfs_version < common_paths.ROOTFS_MIN_VERSION:

            common_utils.print_fatal(
                "Incompatible version found. Please re-run snr with --reinit"
            )
        elif rootfs_version != common_paths.ROOTFS_CURRENT_VERSION:
            common_utils.print_warning(
                "It is advised to re-run snr with --reinit"
            )
    else:
        options.initializing = True
        init.init_main()
        options.initializing = False

    if init_only:
        sys.exit(0)


def _setup_shell() -> None:
    common_utils.print_debug("Registering atexit callbacks")
    atexit_callbacks.register_atexit_callbacks()
    os.chdir(pathlib.Path(__file__).parents[1] / "payloads")
    common_utils.print_debug("Registering commands")
    from snr.cli.commands import (  # pylint: disable=unused-import,import-outside-toplevel
        filesystem, misc, payload, variable)


@click.command(name="snr")
@click.option("--verbose", "-v",
              is_flag=True,
              default=options.verbose,
              envvar="SNR_VERBOSE",
              help="Be more verbose, show debug level logs"
              )
@click.option("--quiet", "-q",
              is_flag=True,
              default=options.quiet,
              envvar="SNR_QUIET",
              help="Be more quiet, Suppress info level logs"
              " and initial banner"
              )
@click.option("--arch", "payload_arch",
              type=click.Choice(["i386", "x86_64"], False),
              default=arch.get_arch(),
              show_default=True,
              envvar="SNR_ARCH",
              help="Set architecture to generate payloads for"
              )
@click.option("--init", "do_init",
              default=False,
              is_flag=True,
              show_default=True,
              help="Initialize snr")
@click.option("--reinit", "do_reinit",
              default=False,
              is_flag=True,
              show_default=True,
              help="Force initialize, even if it seems like"
              " initialization has been done before")
@click.option("--init-only",
              default=False,
              is_flag=True,
              show_default=True,
              help="Only initialize, do not start a shell, must be used with --init")
@click.option("--init-if-needed",
              default=False,
              is_flag=True,
              show_default=True,
              help="Initialize if needed, otherwise the flag does nothing")
@click.option("--host-primary-nameserver",
              default=options.default_primary_nameserver,
              show_default=True,
              envvar="SNR_HOST_PRIMARY_NAMESERVER",
              help="Set generated host image's primary DNS nameserver")
@click.option("--host-secondary-nameserver",
              default=options.default_secondary_nameserver,
              show_default=True,
              envvar="SNR_HOST_SECONDARY_NAMESERVER",
              help="Set generated host image's secondary DNS nameserver")
@click.option("--host-hostname",
              default=options.default_hostname,
              show_default=True,
              envvar='SNR_HOST_HOSTNAME',
              help="Set generated host image's hostname")
@click.option("--user-agent",
              default=options.default_user_agent,
              show_default=True,
              envvar="SNR_USER_AGENT",
              help="User agent in case of internet access")
@click.option("--default-exit-code",
              type=int,
              show_default=True,
              default=options.default_exit_code,
              envvar="SNR_DEFAULT_EXIT_CODE",
              help="Set default exit code")
@click.option("--debug",
              default=False,  # Snr interface does not obey the configuration value for debug
              is_flag=True,
              show_default=True,
              help="In the case of something going wrong, drop to a debug shell")
@click.option("--version", "show_version",
              is_flag=True,
              help="Print version information")
def _main(verbose: bool, quiet: bool, payload_arch: str, host_primary_nameserver: str,
          host_secondary_nameserver: str, host_hostname: str, user_agent: str,
          default_exit_code: int, debug: bool, show_version: bool, do_init: bool = False, init_only: bool = False,
          init_if_needed: bool = False, do_reinit: bool = False, **kwargs: Any) -> None:
    """Stick 'n' Run (snr)"""
    common_utils.print_debug("Installing rich traceback handler")
    rich.traceback.install()
    _show_version(show_version)
    _check_for_libsnr()
    common_utils.print_debug("Applying to options")
    options.arch = payload_arch
    options.verbose = (verbose is True and quiet is False) or debug
    options.quiet = (verbose is False and quiet is True) and not debug
    options.default_primary_nameserver = host_primary_nameserver
    options.default_secondary_nameserver = host_secondary_nameserver
    options.default_hostname = host_hostname
    options.default_user_agent = user_agent
    options.default_exit_code = default_exit_code
    options.debug = debug
    console.console.no_color = options.quiet
    console.err_console.no_color = options.quiet
    _handle_init(do_init, do_reinit, init_only, init_if_needed)
    common_utils.print_debug("Setting up shell")
    _setup_shell()
    interactive_shell.interactive_shell()  # pylint: disable=no-value-for-parameter


def main() -> None:
    """Main function of snr"""
    try:
        _main()  # pylint: disable=no-value-for-parameter
    except bdb.BdbQuit:
        pass
    except Exception:  # pylint: disable=broad-exception-caught
        common_utils.handle_exception()
    sys.exit(options.default_exit_code)
