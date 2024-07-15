Rootfs Versions
===============

As Snr becomes more and more advanced, the rootfs also needs to be more equipped to supply it's payloads. Here is a history of all the rootfs versions snr had:

Legacy
------

The legacy version of snr rootfs is based on Debian 12 and belongs to pre-1.0.0 versions of snr and is no longer valid for any post-1.0.0 payloads.
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

.. versionremoved: 1.0.0

Non-legacy versions
-------------------

After snr version 1.0.0, a new approach was used: A continuous addition to the existing rootfs packages to allow creation of a sequenced version-based rootfs history.

v1
^^

It is the first non-legacy version of snr rootfs which is based Ubuntu 22.04 LTS and contains the packages:

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


.. versionadded: 1.0.0
.. deprecated: 1.1.0

v2
^^

It is the second version of snr rootfs which is also based on Ubuntu 22.04 LTS and adds some more packages to the earlier version:

* python3-deprecated
* python3-impacket
* python3-pycryptodome

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
* python3-deprecated
* python3-impacket
* python3-pycryptodome
* python3-rich
* shim-signed
* util-linux
* wireless-tools
* wpasupplicant

.. versionadded: 1.1.0
