"""
Module containing initialization routine for first time of running snr
"""
import atexit
import glob
import os
import shutil
import sys

from libsnr.core import arch, common_paths, options
from libsnr.util.common_utils import (print_debug, print_fatal, print_info,
                                      print_ok, remake_dir)
from libsnr.util.programs.debootstrap import Debootstrap

SUITE = "stable"
COMPONENTS = "main,contrib,non-free,non-free-firmware"
ALL_PACKAGES = "btrfs-progs,console-setup,console-setup-linux,cryptsetup,curl,dbus,dosfstools,e2fsprogs,ethtool,firmware-ath9k-htc,firmware-atheros,firmware-bnx2,firmware-bnx2x,firmware-brcm80211,firmware-linux,firmware-realtek,firmware-zd1211,gdisk,grub-efi-{grub_arch}-signed,grub-pc,initramfs-tools,kmod,linux-image-{kernel_arch},lvm2,net-tools,ntfs-3g,python3,shim-signed,util-linux,wireless-tools,wpasupplicant"
ROOTFS_PATH = os.path.join(common_paths.CACHE_PATH, "rootfs")

def clear_cache():
    """
    Remove the cache directory
    """
    shutil.rmtree(common_paths.CACHE_PATH)


def init_main():
    """
    Snr initialization routine, creates the rootfs and required directories
    """
    answer = input(
        "The initialization routine is not fault tolerant at all.\n"
        "Approximately 200MBs of packages need to be downloaded.\n"
        "Your internet speed effects the initialization time.\n"
        "If the archiving stage is taking too long, it's normal. Do not interrupt it.\n"
        "However it should take less than 10, 15 minutes on ADSL connection.\n"
        "Enter yes to continue: "
    ).lower()
    if answer not in ("y", "yes", "yeah"):
        print_info("Aborting initialization")
        sys.exit(options.default_exit_code)
    print_debug("Registering clear cache atexit callback")
    atexit.register(clear_cache)
    print_info("Creating required directories")

    if os.path.exists(common_paths.CACHE_PATH):
        print_info("Removing existing cache path")
        shutil.rmtree(common_paths.CACHE_PATH)

    if os.path.exists(common_paths.CONFIG_PATH):
        print_info("Removing existing config path")
        shutil.rmtree(common_paths.CONFIG_PATH)

    for directory in [common_paths.CACHE_PATH,
                      ROOTFS_PATH,
                      common_paths.CONFIG_PATH]:
        print_debug(f"Creating directory: {directory}")
        os.makedirs(directory)
    print_debug("Preparing to generate rootfs image")
    debootstrap = Debootstrap()
    debootstrap_options = {
        "arch": arch.get_kernel_arch(),
        "components": COMPONENTS,
        "include": ALL_PACKAGES.format(
            arch=arch.get_arch(),
            kernel_arch=arch.get_kernel_arch(),
            grub_arch=arch.get_grub_arch()),
    }
    print_info("Generating rootfs image")
    debootstrap.invoke(SUITE, ROOTFS_PATH,
                       options=debootstrap_options)
    errorcode = debootstrap.wait()
    if errorcode:
        print_fatal(f"Generating rootfs image failed ({errorcode})")
    print_debug("Cleaning rootfs image")
    shutil.rmtree(os.path.join(
        ROOTFS_PATH, "var", "cache", "apt", "archives"))
    shutil.rmtree(os.path.join(
        ROOTFS_PATH, "usr", "share", "man"))
    shutil.rmtree(os.path.join(
        ROOTFS_PATH, "usr", "share", "doc"))
    # Cleanup initrd
    rootfs_boot_path = os.path.join(ROOTFS_PATH, "boot")
    for entry in glob.glob(os.path.join(rootfs_boot_path, "initrd.img-*")):
        os.remove(entry)
    print_info("Archiving rootfs image")
    shutil.make_archive(common_paths.ROOTFS_ARCHIVE_BASE_PATH,
                        format=common_paths.ROOTFS_ARCHIVE_FORMAT,
                        root_dir=ROOTFS_PATH,
                        base_dir=".")
    remake_dir(ROOTFS_PATH)
    atexit.unregister(clear_cache)
    print_ok("Initialization successful")
