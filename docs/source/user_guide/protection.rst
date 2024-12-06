Protection
==========

Protection from these sorts of attacks comes in only one way. **Protect the boot sequence.** If the boot sequence is compromised, there is no way to stop the payload. So everything must be done to ensure unknown operating systems won't get loaded. UEFI Secure Boot is not a viable option as shim is used. To protect the boot sequence, several measures must be taken in all three of firmware, bootloader and operating system.

Firmware
--------

1. Firmware settings must require a password, otherwise the attacker can manually change the boot sequence from there.

2. Booting from external sources must be disabled. This includes USB/CD/DVD/Network (PXE) boot.

You might wonder why the second one is needed and that is because most firmware allow changing the boot sequence manually for this boot (especially UEFI ones) if the boot fails or the user presses F10 during boot.

Bootloader
----------

1. Bootloader must not automatically discover operating systems on boot, or if that option cannot be disabled. External sources must be blacklisted.

2. Bootloader must protect its boot options using a password or not expose such functionality. As an example, GRUB2 can have users, and its console and entry editing functions can be protected using a password with requiring a valid user's credentials.

Operating System
----------------

1. Automatic login must be not be used. This is likely to let the user a way to change the bootloader's loading sequence from inside the operating system. In simpler words, the attacker must get nothing but a login screen after booting the operating system.

Failure to do any of the above opens your device to attacks. If one is not possible, then your device must not ever leave your side. The less time your device is left without you, the less chance of such attacks. Even with all of the above, protection from such attacks is not 100 percent. Security is never 100 percent. So it's generally a good idea to know who is exactly with your device.
