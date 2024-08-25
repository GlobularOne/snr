Variable Validation
===================

Snr as a framework can help validate the input your payload. This not only helps reducing the amount of boilerplate in your payload but also improves the user experience.

Validation Flags
----------------

.. note:: For variables of type boolean, all validation flags beside `USED_BY_PAYLOAD` are ignored (which is passed automatically, essentially, no rules for booleans.)

.. note:: For variables of type list, unless specified otherwise, the validation rules apply to each of it's elements.

NORMAL
^^^^^^
The default. Value will not be touched at all.

.. note:: You do not need to pass this, lack of a flag defaults to this.

REQUIRED
^^^^^^^^
Variable is required. Meaning that the value at time of validation should be different than the default provided.

.. warning::
    If a payload needs a variable but the default is okay, you should not use this! Snr automatically adds `USED_BY_PAYLOAD`
    to the flags which prevents deletion of the variable from the shell.

USED_BY_PAYLOAD
^^^^^^^^^^^^^^^
Variable is used by a payload and should not be removed by shell commands

.. note:: You do not need to pass this, it will be automatically added.

VALID_STRING
^^^^^^^^^^^^
Value must be non-empty, and not be made of entirely whitespace and cannot contain null bytes.

VALID_ALPHA
^^^^^^^^^^^
Value must be a valid `[a-zA-Z]`.

.. note:: Using this rule automatically implies `VALID_STRING`

VALID_ALPHANUM
^^^^^^^^^^^^^^
Value must be a valid `[a-zA-Z0-9]`.

.. note:: Using this rule automatically implies `VALID_STRING`

VALID_ASCII
^^^^^^^^^^^
Value must be a valid ASCII string.

.. note:: Using this rule automatically implies `VALID_STRING`

VALID_PATH_COMPONENT
^^^^^^^^^^^^^^^^^^^^
Value must be a valid path component. A valid path component doesn't include any dangerous special characters, including `/`.

.. note:: Using this rule automatically implies `VALID_STRING`

VALID_LOCAL_PATH
^^^^^^^^^^^^^^^^
Value must be an existing, readable path in the local machine.

VALID_HOST_PATH
^^^^^^^^^^^^^^^
Value must be an existing, readable path in the host machine.

VALID_PORT
^^^^^^^^^^
Value must be a valid port number.

.. warning::
    This rule is only valid for integers, it will be ignored for any other type.
    This decision was taken to ensure developers don't end up confusing users. In conversion of
    a string to a port number, one may assume the input could be in hex, one would assume they could pass protocol name, etc.

VALID_IP
^^^^^^^^
Value must be a valid IP (Whatever IPv4 or IPv6).

.. note:: By declaring this, users can pass domain names and interface names and snr will automatically get the IP address for you.
.. tip:: If an interface name or domain name is passed, IPv4 will be preferred over IPv6 if both are available. Same is said for domain names.

VALID_IPV4
^^^^^^^^^^
Value must be a valid IPv4

.. note:: By declaring this, users can pass domain names and interface names and snr will automatically get the IP address for you.

VALID_IPV6
^^^^^^^^^^
Value must be a valid IPv6

.. note:: By declaring this, users can pass domain names and interface names and snr will automatically get the IP address for you.

.. tip::
    When to use `VALID_IP` vs `VALID_IPV4` vs `VALID_IPV4`?
    It depends on whatever all of the software that is using the value support IPv6 or not.
    In general, it's recommended to use VALID_IP to not leave out IPv6 but if in the smallest amount of doubt,
    It would be beneficial to use `VALID_IPV4` than risk the payload not functioning at all.
