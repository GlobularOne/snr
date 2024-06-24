Shell Commands
==============

Snr comes with many commands, mostly to help in not exiting the shell to run a command with the system shell and then run snr again.
Full list of commands can be retrieved using `help`, here we list them all, alongside examples to help you understand them better.

*Note that here, the command results are commented out to avoid highlighting issues*

Filesystem commands
-------------------

pwd
^^^

Prints the current working directory:

.. code-block::

    pwd
    # /home/user/workspace

chdir
^^^^^

Changes the current working directory:

.. code-block::

    chdir /home/user/workspace/snr

.. code-block:: 

    pwd
    # /home/user/workspace/snr

list
^^^^

Lists files and directories.
By default lists the content of the current working directory:

.. code-block::

    list
    # file1
    # file2
    # dir1/
    # dir2/

Also accepts a directory to list content of:

.. code-block::

    list /home/user/workspace/my_payloads
    # file12
    # file13

read
^^^^

Reads the content of a file:

.. code-block::

    read /home/user/workspace/data.txt
    # Sample data inside data.txt

checksum
^^^^^^^^

Generate checksum of a file. It's syntax is like this:

    checksum <algorithm> <file>

List of valid algorithms:

* blake2b
* md5
* sha1
* sha224
* sha256
* sha384
* sha512

For example:

.. code-block::

    checksum md5 test.txt
    # d8e8fca2dc0f896fd7cb4cb0031ba249


Variable commands
-----------------

unset
^^^^^

Removes a variable, it's an alternative syntax to `set variable_name` which does the same:

.. code-block::

    unset my_var

set
^^^

See it as variable manager, it allows you to set variables:

.. code-block::

    set my_var my_value


Set also has a special ability, it can tie the output of a command to a variable:

.. code-block::

    set my_var !checksum test.txt

Note that this syntax is only used by set and no other commands support it.

But also can remove them:

.. code-block::

    set my_var

You can also list all variables with it:

.. code-block::

    set

Payload commands
----------------

use
^^^

Use command allows you to load and unload payloads.

To load a payload, pass it's path to use:

.. code-block::

    use misc/run_command
    # [+] Payload loaded

It can also be used to unload a payload:

.. code-block::

    use

You may also reload a payload with just loading the same payload again.

generate
^^^^^^^^

Generates the selected payload onto the device or file you pass to it.

.. code-block::

    generate /dev/sdb


Miscellaneous commands
----------------------

clear
^^^^^

Clears the screen.

.. code-block::

    clear

echo
^^^^

Prints back what you give it. Mostly useful for getting value of variables.

.. code-block::

    echo Snr rocks!
    # Snr rocks!

.. code-block::

    set my_var Snr rocks!
    

.. code-block::

    echo $my_var
    # Snr rocks!

exit
^^^^

Exists the shell, printing whatever you want it to print.

.. code-block::

    exit

The above example prints nothing.


help
^^^^

Can you give you a lot of information.

List of all commands:

.. code-block:: 

    help

Help on a specific command:

.. code-block::

    help checksum

Help on a specific variable (assuming we have loaded the `misc/run_command` payload):

.. code-block::

    help COMMANDS

Help on the loaded payload (again assuming we have loaded the `misc/run_command` payload):

.. code-block::

    help payload
    # Payload path: misc/run_command
    # Input: COMMANDS
    # Authors: GlobularOne
    # License: gpl-3.0
    # Dependencies: No dependencies specified
    # Run a command or executable on boot, the executable must exist on the host filesystem.
    # If you want to run an executable that is locally available. Use run_executable.
    # It finds the executable and copies it onto the host filesystem.

info
^^^^

Alternative syntax for `help payload` (again assuming we have loaded the `misc/run_command` payload):

.. code-block:: 

    info
    # Payload path: misc/run_command
    # Input: COMMANDS
    # Authors: GlobularOne
    # License: gpl-3.0
    # Dependencies: No dependencies specified
    # Run a command or executable on boot, the executable must exist on the host filesystem.
    # If you want to run an executable that is locally available. Use run_executable.
    # It finds the executable and copies it onto the host filesystem.

*Added in version 0.1.0*

pdb
^^^

Drop into a debug shell, useful for debugging if something is misbehaving.
But if it errors out, pass `--debug` to snr, which does the same if something goes wrong

.. code-block:: 

    pdb
    # ...


*Added in version 1.0.0*

reload
^^^^^^

Reloads the shell, note that no state will be saved (variables, loaded payload)

.. code-block::

    reload
    # [!] Reloading shell, shell state will not be saved!
