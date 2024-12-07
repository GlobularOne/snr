Contributing a Payload
======================

Snr comes with many payloads by default, they can be found inside the `snr/payloads` directory of the source code. If you want to contribute your payload. You must take care of a few things:

* It must use the :doc:`entry_point </ref/snr.core.payload.entry_point>` if a python module.
* It must be put under the right category (See :doc:`/user_guide/payload_categories`.)
* If it deals with filesystem, it must have the very same `PASSPHRASES` variable and handle encrypted partitions according to it.
* It must declare `AUTHORS`, `TARGET_OS_LIST`.

If you want to contribute your payload but unsure how to satisfy the above conditions. Just go ahead and create a PR! We will help you with the above conditions.

But if you want to keep the payload private or test it out before adding it to snr's list of builtin payloads. You need to follow this structure:

* Each payload is inside its own directory. It is the payload's own world.
* The payload's generation method (the `Payload` class) must be inside a file named `__init__.py`.
* Any other files the payload uses, should be put inside the payload's directory (so you can use the many utility functions.)
