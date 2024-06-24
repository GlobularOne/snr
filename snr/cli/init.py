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
                         "e2fsprogs", "ethtool", "firmware-ath9k-htc",
                         "linux-firmware", "gdisk", "grub-efi-{grub_arch}-signed", "grub-pc",
                         "initramfs-tools", "kmod", "linux-image-generic",
                         "lvm2", "net-tools", "ntfs-3g",
                         "python3", "python3-rich", "shim-signed",
                         "util-linux", "wireless-tools", "wpasupplicant"])
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


def init_main() -> None:
    """
    Snr initialization routine, creates the rootfs and required directories
    """
    common_utils.print_info("Starting initialization process")
    common_utils.print_debug("Registering clear data atexit callback")
    atexit.register(_clear_data)

    if os.path.exists(common_paths.DATA_PATH):
        common_utils.print_info("Removing existing data path")
        shutil.rmtree(common_paths.DATA_PATH)

    if os.path.exists(common_paths.CACHE_PATH):
        common_utils.print_info("Removing existing cache path")
        shutil.rmtree(common_paths.CACHE_PATH)

    if os.path.exists(common_paths.STATE_PATH):
        common_utils.print_info("Removing existing state path")
        shutil.rmtree(common_paths.STATE_PATH)

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
        debootstrap_options["variant"] = "fakechroot"
    common_utils.print_info("Generating rootfs image")
    errorcode = programs.Debootstrap(
        fakeroot=True, fakechroot=True).invoke_and_wait(None, SUITE, ROOTFS_PATH,
                                                        options=debootstrap_options)
    if errorcode:
        common_utils.print_fatal(
            f"Generating rootfs image failed ({errorcode})")
    common_utils.print_debug("Cleaning rootfs image")
    for trim_dir in TRIM_DIRS:
        shutil.rmtree(trim_dir)
    # Cleanup initrd
    rootfs_boot_path = os.path.join(ROOTFS_PATH, "boot")
    for entry in glob.glob(os.path.join(rootfs_boot_path, "initrd.img-*")):
        os.remove(entry)
    for directory in ["proc", "dev"]:
        os.unlink(os.path.join(ROOTFS_PATH, directory))

    # Fixes on the rootfs, first make the efi directory and a few directories
    for directory in ["boot/efi", "root/.config/snr",
                      "root/.cache/snr", "root/.local/state/snr",
                      "root/.local/share/snr"]:
        os.mkdir(os.path.join(ROOTFS_PATH, directory))

    with open(os.path.join(ROOTFS_PATH, "root/.config/snr/main.conf"),
              "w", encoding="utf-8") as _:
        pass

    if os.getuid() != 0:
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
                        format=common_paths.ROOTFS_ARCHIVE_FORMAT,
                        root_dir=ROOTFS_PATH,
                        base_dir=".")

    common_utils.remake_dir(ROOTFS_PATH)
    atexit.unregister(_clear_data)
    common_utils.print_ok("Initialization successful")
