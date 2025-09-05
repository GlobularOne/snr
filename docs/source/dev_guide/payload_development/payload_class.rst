Payload Class
=============

Now we can see a template for how a snr payload looks like:

.. code-block:: python

    """
    Description of what the payload does
    """
    from snr.core.payload.payload import Context, Payload

    class MyPayload(Payload):
        AUTHORS = ("Me",)
        TARGET_OS_LIST = ...
        INPUT = (
            ...
        )

        def generate(self, ctx: Context) -> int:
            variables = self.get_self_variables()
            ...
            return 0

    payload = MyPayload()

Now let's break it down:

.. code-block:: python

    """
    Description of what payload does
    """
 
This will be the message the user sees when they run `info`. Generally, you should describe whatever the user needs to know here.

.. code-block:: python

    from snr.core.payload.payload import Context, Payload

This line imports the bare minimum that is needed for a file to describe a payload generation. 

.. code-block:: python

    class MyPayload(Payload):

This line declares a new class, all payloads are required to do so.

Payload Class Important Members
-------------------------------

Now each `Payload` subclass, has some requirements and some optional features you can use.

1. `generate()` method. It is the sole requirement.

Payload Class Informational Members
-----------------------------------

Also, you can declare so many information inside the class:

AUTHORS
^^^^^^^

A tuple of all the authors of the payload. If not specified, it is assumed to not have any credits.

LICENSE
^^^^^^^

The SPDX license identifier of the payload's license, if not specified, it is assumed to be `gpl-3.0` (GPLv3.)

INPUT
^^^^^

A tuple, of tuples that describe variables that the user can change (or may be required to do so) to configure the payload.
It is generally in this format:

.. code-block:: python

    (
        (<variable_name>, <default_value>, <max_size>, <documentation>, <flags>),
        ...
    )

* variable_name: The name of the variable itself.
* default_value: Default value for the variable. The variable's type is determined from this and can be either a `str`, `int`, `bool` or a `list` of `str`.
* max_size: the maximum size of the variable, to not specify it, use `-1`. In case the type is `str`, the maximum count of characters that are assumed valid, or in case of a `list`, the maximum number of elements that are considered valid. `int` or `bool` type variables are not allowed to have a max_size in which case `-1` must be used.
* documentation: The documentation or "help value" for the variable, helps the user a lot and is strongly recommended.
* flags: The field itself is optional and can be omitted. It is a mix of all flags, see :doc:`validation`.

DEPENDENCIES
^^^^^^^^^^^^

A tuple of Ubuntu packages that the payload requires to be available in the host to work. See :doc:`rootfs_versions` for the existing list of pre-installed packages.

TARGET_OS_LIST
^^^^^^^^^^^^^^

A tuple of operating systems that are valid targets. It is purely informational and its only usage is for the user to know what OS the payload can target. As it is purely informational, there is no standard about its content however there is a de-facto standard about it:

* If it does not care about the target OS, (because it works irrelevant of the operating system, for example, `tampering/disk_encryption`). You may use `Any`.
* The general recommended format is OS's official name followed by whatever in parenthesis if there needs to be any other detail the user needs to know. For example:
* `GNU/Linux`: It says it works on any Linux distribution.
* `GNU/Linux (Debian-derivatives)`: It says it works on any Debian-based Linux distributions.
* `Microsoft Windows`: It says it works on any Windows, no matter the edition or the version.
* `Microsoft Windows (XP SP1 or later)`: It says it works on any windows released after XP's first Service Pack.
* You can put whatever criteria you want in there, these are just some examples. 

Payload Class Optional Methods
------------------------------

There are also some optional methods you can declare:

* `load()`: It is called when the payload is loaded, **be careful to do `super().load()` if defining this function** as many things are handled there for you there.
* `unload()`: It is called when the payload is to be unloaded, unlike `load()` you do not need to ensure you call `super().unload()` as it does nothing.

Example
-------

With knowing all this, let's put them all to use. Here below is a more complete example using all of the optional features.

.. code-block:: python

    """
    Example payload using all the optional features
    """
    from snr.core.payload.payload import Context, Payload, REQUIRED
    from snr.core.util import common_utils

    class AllFeaturesPayload(Payload):
        AUTHORS = ("GlobularOne",)
        LICENSE = "Apache-2.0"
        TARGET_OS_LIST = ("Microsoft Windows (XP SP1 or later)", "GNU/Linux (Kernel version above 5.0.0)")
        INPUT = (
            ("foo", "bar", 3, "Foo or bar"),
            ("spam", [], 12, "12 Spams", REQUIRED)
        )

        def load(self) -> int:
            # Do whatever you need here
            return super().init()

        def generate(self, ctx: Context) -> int:
            variables = self.get_self_variables()
            if variables['foo'] not in ('foo', 'bar'):
                common_utils.print_error("You have not chosen foo or bar. Unacceptable")
                return 1
            common_utils.print_info(f"You have chosen {variables['foo']} from 'foo' or 'bar'")
            common_utils.print_info(f"Your 12 most elite spams are {variables['spam']}")
            return 0

        def unload(self) -> int:
            return 0

    payload = AllFeaturesPayload()
