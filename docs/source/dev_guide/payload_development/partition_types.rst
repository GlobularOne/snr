Partition Types
===============

When you open a partition (See :doc:`/ref/snr.core.payload.storage`), you can use the `partition_type()` function to retrieve what kind of partition is it. Partitions are split into several categories:

* EFI_PARTITION: Contains EFI boot files.
* BOOT_PARTITION: Contains bootloader files.
* SYSTEM_PARTITION: Contains system files.
* DATA_PARTITION: Contains user data.
* LINUX_PARTITION: Partition with Linux structure.
* WINDOWS_PARTITION: Partition with Windows structure.


Partition Detection Criteria
----------------------------

Here is how to interpret them in simple language:

* EFI_PARTITION: ESP
* BOOT_PARTITION: ESP or partition containing GRUB files
* SYSTEM_PARTITION: `/` for Linux and `C:` for Windows (Or whatever partition Windows is installed to)
* DATA_PARTITION: Any partition that isn't one of above 
* LINUX_PARTITION: `/` of Linux
* WINDOWS_PARTITION: `C:` for Windows

Examples
--------

Let's see some examples on what each partition would be called in some possible disk layouts.

Windows Machine (UEFI)
^^^^^^^^^^^^^^^^^^^^^^

* ESP: `EFI_PARTITION | BOOT_PARTITION`
* NTFS Partition: `SYSTEM_PARTITION | DATA_PARTITION | WINDOWS_PARTITION`

Windows Machine (BIOS)
^^^^^^^^^^^^^^^^^^^^^^

* NTFS Partition: `SYSTEM_PARTITION | DATA_PARTITION | WINDOWS_PARTITION`

Simple Linux Machine (UEFI)
^^^^^^^^^^^^^^^^^^^^^^^^^^^

* ESP: `EFI_PARTITION | BOOT_PARTITION`
* Partition for `/`: `SYSTEM_PARTITION | DATA_PARTITION | LINUX_PARTITION`

Encrypted Linux Machine (UEFI)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* ESP: `EFI_PARTITION | BOOT_PARTITION`
* Partition for `/boot`: `BOOT_PARTITION`
* Partition for `/`: `SYSTEM_PARTITION | DATA_PARTITION | LINUX_PARTITION`

FDE Linux Machine (UEFI)
^^^^^^^^^^^^^^^^^^^^^^^^

* ESP: `EFI_PARTITION | BOOT_PARTITION`
* Partition for `/`: `SYSTEM_PARTITION | DATA_PARTITION | LINUX_PARTITION`

Linux Machine With Separate home (UEFI)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* ESP: `EFI_PARTITION | BOOT_PARTITION`
* Partition for `/`: `SYSTEM_PARTITION | DATA_PARTITION | LINUX_PARTITION`
* Partition for `/home`: `DATA_PARTITION`

Simple Linux Machine (BIOS)
^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Partition for `/`: `BOOT_PARTITION | SYSTEM_PARTITION | DATA_PARTITION | LINUX_PARTITION`

Linux Machine With Separate GRUB (BIOS)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Partition for `/boot`: `BOOT_PARTITION`
* Partition for `/`: `SYSTEM_PARTITION | DATA_PARTITION | LINUX_PARTITION`

Examples Summary
^^^^^^^^^^^^^^^^

In summary:

* If you saw `EFI_PARTITION` it's obviously for ESP.
* If you saw `BOOT_PARTITION`, it may or may not be ESP but contains boot files. (Check for existence of `EFI_PARTITION` flag.)
* If you saw `SYSTEM_PARTITION`, it definitely contains system data, may or may not contains user data as well. (Check for... `DATA_PARTITION`?)
* If you saw `DATA_PARTITION`, it definitely contains user data, may or may not contain system data. (You know the drill.)
* If you saw `LINUX_PARTITION`, it definitely contains Linux structure like `/etc`.
* If you saw `WINDOWS_PARTITION`, it definitely contains Windows structure like `Windows`.

Details
-------

Here is the criteria for each (if you want a complex answer):

* `EFI_PARTITION`: Contains a directory named `EFI` that is not empty.
* `BOOT_PARTITION`: If `EFI_PARTITION` or contains a `/boot` partition that at least contains `grub` directory, `vmlinuz` or `initrd.img` files.
* `SYSTEM_PARTITION`: If `LINUX_PARTITION` or `WINDOWS_PARTITION`.
* `DATA_PARTITION`: If not `EFI_PARTITION`.
* `LINUX_PARTITION`: If `/etc/os-release`, `/etc/lsb-release` or `/etc/shadow` exist.
* `WINDOWS_PARTITION`: If `Windows\\System32` exists.

How to Use the Flags
--------------------

Assuming you mount a partition and the end result is a variable called `mounted_part`. You won't need to use the flags directly. You can use the set of functions we provide:

* `EFI_PARTITION`: `.is_efi()`
* `BOOT_PARTITION`: `.is_boot()`
* `SYSTEM_PARTITION`: `.is_system()`
* `DATA_PARTITION`: `.is_data()`
* `LINUX_PARTITION`: `.is_linux()`
* `WINDOWS_PARTITION`: `.is_windows()`

.. code-block:: python

    if mounted_part.is_system():
        # Deal with system partitions
    ...
