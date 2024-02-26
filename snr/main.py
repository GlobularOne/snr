"""
Module containing the main function, the glue code of snr
"""
import argparse
import os
import shutil
import sys

import requests
from libsnr import version as libsnr_version
from libsnr.core import arch, common_paths, options
from libsnr.util.coloring import BLUE, GREEN, RED, RESET, fore_blue, fore_reset
from libsnr.util.common_utils import (print_debug, print_fatal, print_info,
                                      print_sys, print_warning)
from pyfiglet import Figlet

from snr import atexit_callbacks, command_utils, commands, init, version

try:
    import readline as _
except ImportError:
    pass


REQUIRED_FEATURE_LEVEL = 0


def _app_loop():
    """
    Main application loop
    """
    while True:
        try:
            cmdline = input(
                f"\n{GREEN}{options.prompt}{RESET} ").strip()
            output = command_utils.dispatch_command(cmdline)
            if output is not None:
                print(output, end="")
        except EOFError:
            print("")
        except KeyboardInterrupt:
            print("")
            print_fatal("Exiting...")


def _parse_arguments():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", "-V",
                        action="store_const",
                        dest="verbosity", const=True, default=None,
                        help="Be more verbose, show debug level logs"
                        )
    parser.add_argument("--quiet", "-q",
                        action="store_const",
                        dest="verbosity", const=False, default=None,
                        help="Be more quiet, Suppress info level logs"
                        " and initial banner"
                        )
    parser.add_argument("--arch",
                        action="store", choices=("i386", "x86_64"),
                        default=arch.get_arch(),
                        help="Set architecture to generate payloads for"
                        )
    parser.add_argument("--init",
                        action="store_true",
                        help="Initialize snr")
    parser.add_argument("--reinit",
                        action="store_true",
                        help="Force initialize, even if it seems like"
                        " initialization has been done before")
    parser.add_argument("--update-payload-set", action="store_true",
                        help="Update snr's payload set. Using either --init or"
                        " --reinit implies this option")
    parser.add_argument("--code", "-c", action="store",
                        help="Run code instead of interactive input")
    parser.add_argument("--version", "-v", action="store_true",
                        help="Print version information")
    if version.DEVELOPMENT:
        dev_argument_group = parser.add_argument_group(
            "Development arguments",
            description="These arguments are only intended to be used only in development")
        dev_argument_group.add_argument("--enable-development-mode",
                                        action="store_true",
                                        help="Enable development mode, enables development options,"
                                        " disables quiet mode and enables verbose mode")
        dev_argument_group.add_argument("--dry-payload-set-update",
                                        action="store_true",
                                        help="If attempted to update the payload set,"
                                        " do actually nothing")
        dev_argument_group.add_argument("--ignore-compatibility-issues",
                                        action="store_true",
                                        help="Ignore if snr's version major doesn't match"
                                        " libsnr's version major")
        dev_argument_group.add_argument("--force-interactive-mode",
                                        action="store_true",
                                        help="Even if -c is passed on the command line,"
                                        " still assume the program is being run interactively."
                                        " This is a VERY DANGEROUS option and should not"
                                        " be taken lightly")
    return parser.parse_args(sys.argv[1:])


def _dev_option_enabled(namespace, option):
    if namespace.enable_development_mode:
        if option:
            return True
    return False


def _download_payload_set(set_version: str):
    with open(os.path.join(common_paths.CACHE_PATH, "payload_set.tar.gz"), "wb") as stream:
        headers = {'User-Agent': 'Mozilla/5.0'}
        payload_set = requests.get(
            "https://github.com/GlobularOne/snr_payloads/releases/download/"
            f"{set_version}/payload_set.tar.gz", headers=headers)
        if payload_set.status_code == 200:
            stream.write(payload_set.content)
        else:
            print_fatal(
                "Downloading payload set archive failed"
                f" with status code ({payload_set.status_code})")


def _update_payload_set(namespace):
    if not _dev_option_enabled(namespace, namespace.dry_payload_set_update):
        print_debug("Fetching latest version info")
        latest_version = requests.get(
            "https://github.com/GlobularOne/snr_payloads/releases/latest").url.split("/")[-1]
        if os.path.exists(os.path.join(common_paths.CONFIG_PATH, "payload_version")):
            with open(os.path.join(common_paths.CONFIG_PATH, "payload_version"),
                      encoding="utf-8") as stream:
                installed_version = stream.readline().strip()
            if installed_version != latest_version:
                print_info(
                    f"Version '{installed_version}' is already installed,"
                    f" but the latest is '{latest_version}'. Installing...")
                _download_payload_set(latest_version)
            else:
                print_info("Latest version already installed")
        else:
            print_info(
                f"No version is installed, but the latest is '{latest_version}'. Installing...")
            _download_payload_set(latest_version)

        print_debug("Clearing payload_set directory")
        shutil.rmtree(os.path.join(common_paths.CACHE_PATH,
                      "payload_set"), ignore_errors=True)
        print_debug("Unpacking payload set")
        shutil.unpack_archive(os.path.join(common_paths.CACHE_PATH, "payload_set.tar.gz"),
                              os.path.join(common_paths.CACHE_PATH, "payload_set"), "gztar")
        print_debug("Payload set installed successfully")
    else:
        # Still ensure the payload_set directory exists
        os.mkdir(os.path.join(common_paths.CACHE_PATH, "payload_set"))


def _count_payloads():
    try:
        count = 0
        payload_set_dir = os.path.join(common_paths.CACHE_PATH, "payload_set")
        dir_content = os.listdir(payload_set_dir)
        for content in dir_content:
            path = os.path.join(payload_set_dir, content)
            if os.path.isfile(path) and path.endswith(".py"):
                count += 1
        return count

    except Exception:  # pylint: disable=broad-exception-caught
        return 0


def _check_environment(namespace):
    if libsnr_version.MAJOR != version.MAJOR or int(libsnr_version.MINOR) < REQUIRED_FEATURE_LEVEL:
        print(
            "Incompatible version of libsnr found."
            f" libsnr version {libsnr_version.__version__} is not"
            f" compatible with snr version {version.MAJOR}", end="")
        if not _dev_option_enabled(namespace, namespace.ignore_compatibility_issues):
            print("")
            sys.exit(1)
        else:
            print("... Ignoring as requested")
    if os.getuid() != 0:
        print("Please run snr as root")
        sys.exit(1)


def _parse_options(namespace):
    options.arch = namespace.arch
    options.verbose = namespace.verbosity is True
    options.quiet = namespace.verbosity is False
    options.interactive = True if _dev_option_enabled(
        namespace, namespace.force_interactive_mode) else namespace.code is None
    if _dev_option_enabled(namespace, namespace.enable_development_mode):
        options.verbose = True
        options.quiet = False
    code = namespace.code
    common_paths.format_rootfs_archive_path(arch.get_arch())
    should_initialize = False
    if namespace.init or namespace.reinit:
        namespace.update_payload_set = True
    if namespace.reinit:
        if namespace.init:
            # Just issue a warning that this combination
            # doesn't sound very valid
            print_warning("--init and --reinit used together")
        should_initialize = True
    elif not os.path.exists(common_paths.ROOTFS_ARCHIVE_PATH):
        # Are we allowed to initialize
        if namespace.init:
            should_initialize = True
        else:
            print_fatal("Please re-run snr with --init to initialize")
    return code, should_initialize


def main():
    """
    Main function of snr user interface
    """
    namespace = _parse_arguments()
    if namespace.version:
        print(
            f"snr version {version.MAJOR} (libsnr version {libsnr_version.__version__})")
        sys.exit(0)
    if not hasattr(namespace, "enable_development_mode"):
        namespace.enable_development_mode = False
        namespace.dry_payload_set_update = False
        namespace.ignore_compatibility_issues = False
        namespace.force_interactive_mode = False
    _check_environment(namespace)
    code, should_initialize = _parse_options(namespace)
    if not options.quiet:
        fore_blue()
        print(Figlet(font="slant").renderText("stick->'n'->run"))
        print_sys(
            f"{BLUE}Version{RESET}: {RED}{version.__version__}"
            f" (Library version: {libsnr_version.__version__})")
        print_sys(
            f"{BLUE}Homepage{RESET}: {RED}{version.HOMEPAGE}")
        print_sys(
            f"{RED}{_count_payloads()}{BLUE} Available Payloads"
        )
        fore_reset()
    if should_initialize:
        options.initializing = True
        init.init_main()
        options.initializing = False
    if namespace.update_payload_set:
        _update_payload_set(namespace)
    del namespace
    print_debug("Registering atexit callbacks")
    atexit_callbacks.register_atexit_callbacks()
    os.chdir(os.path.join(common_paths.CACHE_PATH, "payload_set"))
    print_debug("Registering commands")
    command_utils.commands = commands.discover_commands()
    if code is not None:
        for line in code.split(";"):
            output = command_utils.dispatch_command(line)
            if output is not None:
                print(output)
        return
    _app_loop()
