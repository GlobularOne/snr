"""
Initialization routine for first time of running snr (or for reinit)
"""
import atexit
import glob
import os
import shutil

from snr.core.core import arch, common_paths
from snr.core.util import common_utils, programs

__all__ = (
    "init_main",
)

SUITE = "jammy"
COMPONENTS = ",".join(["main", "multiverse", "restricted", "universe"])
ALL_PACKAGES = ",".join(["btrfs-progs", "console-setup", "console-setup-linux",
                         "cryptsetup", "curl", "dbus", "dosfstools",
                         # Workaround for https://github.com/GlobularOne/snr/issues/3
                         "python3-cffi-backend",
                         "e2fsprogs", "ethtool", "firmware-ath9k-htc",
                         "linux-firmware", "gdisk", "grub-efi-{grub_arch}-signed", "grub-pc",
                         "initramfs-tools", "kmod", "linux-image-generic",
                         "lvm2", "net-tools", "ntfs-3g",
                         "python3", "python3-deprecated", "python3-impacket", "python3-pycryptodome", "python3-rich",
                         "shim-signed", "util-linux", "wireless-tools", "wpasupplicant"])
ROOTFS_PATH = os.path.join(common_paths.DATA_PATH, "rootfs")
TRIM_DIRS = (
    os.path.join(
        ROOTFS_PATH, "var", "cache", "apt", "archives"),
    os.path.join(
        ROOTFS_PATH, "usr", "share", "man"),
    os.path.join(
        ROOTFS_PATH, "usr", "share", "doc")
)


def _clear_data() -> None:
    """
    Remove the data directory
    """
    shutil.rmtree(common_paths.DATA_PATH)


def _handle_required_directories() -> None:

    common_utils.print_debug("Looking for directories that should be cleaned")

    for path in (common_paths.DATA_PATH, common_paths.CACHE_PATH, common_paths.STATE_PATH):
        common_utils.print_info(f"Removing path: {path}")
        shutil.rmtree(path, ignore_errors=True)
    # Preserve config path

    common_utils.print_info("Creating required directories")

    for directory in [
            ROOTFS_PATH,
            common_paths.DATA_PATH,
            common_paths.CONFIG_PATH,
            common_paths.STATE_PATH,
            common_paths.CACHE_PATH]:
        common_utils.print_debug(f"Creating directory: {directory}")
        os.makedirs(directory, exist_ok=True)


def _generate_rootfs() -> None:
    common_utils.print_debug("Preparing to generate rootfs image")
    debootstrap_options = {
        "arch": arch.get_kernel_arch(),
        "components": COMPONENTS,
        "include": ALL_PACKAGES.format(
            arch=arch.get_arch(),
            kernel_arch=arch.get_kernel_arch(),
            grub_arch=arch.get_grub_arch()),
    }
    if os.getuid() != 0:
        common_utils.print_debug("Using fakechroot variant")
        debootstrap_options["variant"] = "fakechroot"
    common_utils.print_info("Generating rootfs image")
    errorcode = programs.Debootstrap(
        fakeroot=True, fakechroot=True).invoke_and_wait(None, SUITE, ROOTFS_PATH,
                                                        options=debootstrap_options)
    if errorcode:
        common_utils.print_fatal(
            f"Generating rootfs image failed ({errorcode})")


def _archive_post_process() -> None:
    common_utils.print_debug("Cleaning rootfs image")
    for trim_dir in TRIM_DIRS:
        shutil.rmtree(trim_dir)
    common_utils.print_debug("Cleaning up initrd images")
    rootfs_boot_path = os.path.join(ROOTFS_PATH, "boot")
    for entry in glob.glob(os.path.join(rootfs_boot_path, "initrd.img-*")):
        os.remove(entry)

    # If using fakechroot, it creates absolute links to the system's directories
    # If we let them pass to the second fix below which converts them to relative,
    # it will simply break. So we must fix them manually.
    common_utils.print_debug(
        "Checking if /proc, /sys, and /dev need to be fixed inside rootfs")
    for directory in ["proc", "sys", "dev"]:
        if os.path.islink(os.path.join(ROOTFS_PATH, directory)):
            common_utils.print_debug(
                f"/{directory} needs to be fixed, doing so")
            os.unlink(os.path.join(ROOTFS_PATH, directory))
            os.mkdir(os.path.join(ROOTFS_PATH, directory))

    # Fixes on the rootfs, first make the efi directory and a few directories
    common_utils.print_debug(
        "Creating some required directories inside rootfs")
    for directory in ["boot/efi", "root/.config/snr",
                      "root/.cache/snr", "root/.local/state/snr",
                      "root/.local/share/snr"]:
        common_utils.print_debug(f"Creating /{directory} inside rootfs")
        os.makedirs(os.path.join(ROOTFS_PATH, directory), exist_ok=True)

    common_utils.print_debug("Creating config file inside rootfs")
    with open(os.path.join(ROOTFS_PATH, "root/.config/snr/main.conf"),
              "w", encoding="utf-8") as _:
        pass

    if os.getuid() != 0:
        common_utils.print_debug(
            "Fakechroot used during generation process, fixing up all symlinks")
        # Second, convert all absolute links into relative ones
        # Because if fakechroot was used, all the links are absolute
        for root, _, files in os.walk(ROOTFS_PATH):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                if os.path.islink(file_path) and os.path.isabs(os.readlink(file_path)):
                    link_target = os.readlink(file_path)
                    relative_path = os.path.relpath(
                        link_target, start=os.path.dirname(file_path))
                    os.unlink(file_path)
                    os.symlink(relative_path, file_path)

    common_utils.print_info("Archiving rootfs image")
    shutil.make_archive(common_paths.ROOTFS_ARCHIVE_BASE_PATH,
                        format=common_paths.ROOTFS_ARCHIVE_FORMAT.split(":")[
                            1] + "tar",
                        root_dir=ROOTFS_PATH,
                        base_dir=".")
    common_utils.print_debug("Creating rootfs image's .version file")
    with open(common_paths.ROOTFS_ARCHIVE_VERSION_PATH, "w", encoding="utf-8") as stream:
        stream.write(str(common_paths.ROOTFS_CURRENT_VERSION))


def init_main() -> None:
    """
    Snr initialization routine, creates the rootfs and required directories
    """
    common_utils.print_info("Starting initialization process")
    common_utils.print_debug("Registering clear data atexit callback")
    atexit.register(_clear_data)

    _handle_required_directories()
    _generate_rootfs()
    _archive_post_process()

    common_utils.print_debug("Cleaning up rootfs directory")
    common_utils.remake_dir(ROOTFS_PATH)
    common_utils.print_debug("Unregistering clear data atexit callback")
    atexit.unregister(_clear_data)
    common_utils.print_ok("Initialization successful")
