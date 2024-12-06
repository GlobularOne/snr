Configuration
=============

Snr can not only be configured at runtime using flags, but also using environment variables and the config file.

Here, you will find a list of configuration keys and some help on them.

The configuration file can be found in `~/.config/snr/main.conf`.
We use the INI format, all snr configuration are inside the `[main]` section.

Configuration Priority
----------------------

If configuration can come from 3 sources, which have priority over the other?

1. command line options 
2. environment variables
3. configuration file

Meaning, command line options can override both environment variables and configuration in the file, and neither of those can override command line options.

Configuration Keys
------------------

verbose
^^^^^^^

Controls the verbosity.

**Type: boolean**

**Default: off**

**Env var: SNR_VERBOSE**

quiet
^^^^^

Controls whatever informational messages are shown or not. Also suppresses the initial banner.

**Note: Setting both quiet and verbose as on will cancel each other out**

**Type: boolean**

**Default: off**

**Env var: SNR_QUIET**

arch
^^^^

Architecture of the generated image. Either `i386` or `x86_64`.

**Type: string**

**Default: Determined on runtime**

**Env var: SNR_ARCH**


default_exit_code
^^^^^^^^^^^^^^^^^

Default exit code of snr when the user runs `exit`, also used by other functions to exit normally.

**Type: integer**

**Default: 0**

**Env var: SNR_DEFAULT_EXIT_CODE**


default_hostname
^^^^^^^^^^^^^^^^

Sets the default hostname of the generated host OS.

**Type: string**

**Default: "snr"**

**Env var: SNR_HOST_HOSTNAME**

default_primary_nameserver
^^^^^^^^^^^^^^^^^^^^^^^^^^

Sets the primary nameserver (primary DNS server) of the generated host OS.

**Type: IP address (v4 only)**

**Default: "1.1.1.1"**

**Env var: SNR_HOST_PRIMARY_NAMESERVER**

default_secondary_nameserver
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Sets the secondary nameserver (secondary DNS server) of the generated host OS.

**Type: IP address (v4 only)**

**Default: "1.0.0.1"**

**Env var: SNR_HOST_PRIMARY_NAMESERVER**

default_user_agent
^^^^^^^^^^^^^^^^^^

Sets the default user agent for download operations.

**Type: string**

**Default: "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0"**

**Env var: SNR_USER_AGENT**

.. versionadded:: 1.1.0
