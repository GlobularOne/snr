Deeper Introduction
===================

:doc:`quickstart` barely scratches the surface of all there is to snr. Here we will dig a bit deeper into snr's interface so you could use it easier.

Verbosity
---------

If you want to get a better idea of how it works inside, you can run snr with `-v` flag to increase verbosity.

Message Symbols
---------------

Each message is categorized by a character known as its symbol, and a color as well:

* Debug: Debug messages use the symbol `.` and the color magenta.

* Info: Those messages use the symbol `!` and the color blue.

* OK: Symbol `+` is used with the color green.

* Warning: Its symbol is `*` and uses color yellow.

* Error: Symbol is `-` and uses color red.

The colors are used in a way that even if one doesn't remember the symbols, you could easily tell the type of message by them.

And also there are some special messages, called system messages. They are from internals of snr and commands don't use them, most commonly you might see them with configuration issues or using an unknown command. They use the symbol `-->` and use no color.

`--init-if-needed` and `--init-only`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

These flags are used to control how snr deals with the initialization process. 
`--init-only` only initializes and does not start the shell. Useful if you only want to initialize snr.
`--init-if-needed` tells snr to initialize if it needs to (it has not been initialized or if it is recommended to initialize again).
So it would be safe to run snr with `--init-if-needed` all the time to ensure you are using the latest of everything (and don't forget to update snr itself): 

.. code-block:: shell

    snr --init-if-needed

Reality of Payloads
-------------------

The payload loading mechanism is kept simple and effective.
Every payload is essentially a directory (python module) with some requirements.
By changing the current working directory, you could load your own custom payloads. (See more about that: :doc:`/dev_guide/payload_development/develop_your_own`)

Advanced Variable Management
----------------------------

Variables do not need to be declared by payloads, you can define them as well using set:

.. code-block::

    set my_variable my_value

But what if we wanted to set its value from the output of a command?

.. code-block::

    set !my_variable read message.txt

The `!` tells set to execute the value, and take the result of it as the new value.

Payload Unloading
-----------------

You can unload a payload using:

.. code-block::

    use

But if you want to switch between payloads (you should have read the faq first):

.. code-block::

    use new_payload

Variables
---------

Variables can expand as well:

.. code-block::

    echo $var

but not as the command itself. Example:

.. code-block::

    set var echo

Now:

.. code-block::

    $var $var

Will just error out. (As you can see as well.) Because it will expand to `$var echo` and `$var` is not a valid command.

.. seealso::

    :doc:`configuration`
        Snr's behavior can be configured with a configuration file as well.
