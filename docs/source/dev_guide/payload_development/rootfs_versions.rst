Rootfs Versions
===============

As Snr becomes more and more advanced, the rootfs also needs to become more equipped to supply its payloads. Here is a history of all the rootfs versions snr had:

Legacy
------

The legacy version of snr rootfs is based on Debian 12 and belongs to pre-1.0.0 versions of snr. It is no longer valid for any post-1.0.0 payloads.
It contains the packages:

* btrfs-progs
* console-setup
* console-setup-linux
* cryptsetup
* curl
* dbus
* dosfstools
* e2fsprogs
* ethtool
* firmware-ath9k-htc
* firmware-atheros
* firmware-bnx2
* firmware-bnx2x
* firmware-brcm80211
* firmware-linux
* firmware-realtek
* firmware-zd1211
* gdisk
* grub-efi-signed
* grub-pc
* initramfs-tools
* kmod
* linux-image
* lvm2
* net-tools
* ntfs-3g
* python3
* shim-signed
* util-linux
* wireless-tools
* wpasupplicant

.. versionremoved:: 1.0.0

Non-legacy versions
-------------------

After snr version 1.0.0, a new approach was used: A continuous addition to the existing rootfs packages to allow creation of a sequenced version-based rootfs history.

v1
^^

It is the first non-legacy version of snr rootfs which is based on Ubuntu 22.04 LTS and contains the packages:

* btrfs-progs
* console-setup
* console-setup-linux
* cryptsetup
* curl
* dbus
* dosfstools
* e2fsprogs
* ethtool
* firmware-ath9k-htc
* linux-firmware
* gdisk
* grub-efi-signed
* grub-pc
* initramfs-tools
* kmod
* linux-image-generic
* lvm2
* net-tools
* ntfs-3g
* python3
* python3-rich
* shim-signed
* util-linux
* wireless-tools
* wpasupplicant

**This verison of rootfs is faulty and should not be used**

.. versionadded:: 1.0.0
.. versionremoved:: 1.1.0

v2
^^

It is the second version of snr rootfs which is also based on Ubuntu 22.04 LTS and adds some more packages to the earlier version:

* python3-deprecated
* python3-impacket
* python3-pycryptodome
* python3-cffi-backend

The full list of packages are:

* btrfs-progs
* console-setup
* console-setup-linux
* cryptsetup
* curl
* dbus
* dosfstools
* e2fsprogs
* ethtool
* firmware-ath9k-htc
* linux-firmware
* gdisk
* grub-efi-signed
* grub-pc
* initramfs-tools
* kmod
* linux-image-generic
* lvm2
* net-tools
* ntfs-3g
* python3
* python3-cffi-backend
* python3-deprecated
* python3-impacket
* python3-pycryptodome
* python3-rich
* shim-signed
* util-linux
* wireless-tools
* wpasupplicant

**This version of snr rootfs has been removed because it uses old Ubuntu 22.04**

.. versionadded:: 1.1.0
.. versionremoved:: 1.5.0

v3
^^

The third version of snr rootfs. Based on Ubuntu 24.04 LTS and adds some more packages:

* python3-psutil
* nmap
* usbutils
* pciutils

The full list of packages are:

* btrfs-progs
* console-setup
* console-setup-linux
* cryptsetup
* curl
* dbus
* dosfstools
* e2fsprogs
* ethtool
* firmware-ath9k-htc
* gdisk
* grub-efi-signed
* grub-pc
* initramfs-tools
* kmod
* linux-firmware
* linux-image-generic
* lvm2
* nmap
* net-tools
* ntfs-3g
* pciutils
* python3
* python-cffi-backend
* python3-deprecated
* python3-impacket
* python3-psutil
* python3-pycryptodome
* python3-rich
* shim-signed
* usbutils
* util-linux
* wireless-tools
* wpasupplicant

.. versionadded:: 1.5.0
