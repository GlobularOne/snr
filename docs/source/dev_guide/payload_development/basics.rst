Payload Development Basics
==========================

About the Generation Process
----------------------------

Snr generates payload in a methodical way:

1. First the payload is loaded, it gathers whatever information it needs in its load function and declares variables the user can change (and may be required to do so.)
2. User sets variables needed by the payload.
3. User runs generate command which starts the next generation process.
4. Snr does pre-generation steps, including preparing an environment for the payload to generate.
5. Snr calls the payload's generate function, allowing the payload to check and generate.
6. The payload, generates, modifying the environment created for it.
7. Snr does post-generation steps.

Then we will introduce you to some of the under-the-hood mechanisms that exist in snr for payloads.

Safety Pin
----------

Safety pin is a mechanism that exists in snr to ensure payloads only run inside an environment they are intended to be run in, a proper host.
This ensures users cannot accidentally run payloads on their own local machine and cause some serious damage.
Do note that safety pin does not grant immunity to any target machine and simply only checks for its own host, not any target.

Rootfs
------

Your payload, will eventually run in an environment known to be the host.
However, the host is generated as well and the rootfs is the very skeleton of it.
Any artifacts your payload loads onto it will end up in the final host.

`/data` Directory
-----------------

the `/data` directory inside the host is a directory guaranteed to be writable, even if the whole filesystem is not (in which case whatever written to it will be lost).
It can be used to copy whatever data from the target.

LVM Support
-----------

Once using a Payload Entry Point, we automatically setup LVM so you can use LVM partitions without having to worry about the setup.

LUKS and BitLocker Support
--------------------------

Snr contains utilities to open a partition, supporting opening partitions encrypted with LUKS or BitLocker. 

Payload Entry Point
-------------------

Payload entry point is the entry point of the payload when ran inside the host. It handles setting up the `/data` directory and checks for safety pin so you don't have to worry about them.
