Deeper Introduction
===================

The :doc:`quickstart` barely scratches the surface of all snr is. Here we will dig a bit deeper into snr's interface so you could use it easier.

Verbosity
---------

If you want to get a better idea of how it works inside, you can run snr with `-v` flag to increase verbosity.

Message symbols
---------------

Each message is categorized by a character known as it's symbol, and a color:

* Debug: Debug messages use the symbol `.` and the color magenta

* Info: Those messages use the symbol '!' and the color blue

* OK: Symbol `+` is used with color green

* Warning: It's symbol is `*` and uses color yellow

* Error: Symbol is `-` and uses color red

The colors are used in a way that even if one doesn't remember the symbols, they could easily tell the type of message by them.

And also there are some special messages, called system messages. They are from internals of snr and commands don't use them, most commonly you might see them with configuration issues or using an unknown command. They use symbol `-->` and no color.

Reality of payloads
-------------------

The payload loading mechanism is kept simple and effective.
Every payload is essentially a directory (python module) with some requirements.
By changing the current working directory, you could load your own payloads

Advanced variable management
----------------------------

Variables do not need to be declared by payloads, you can define them as well using set:

.. code-block::

    set my_variable my_value

But what if we wanted to set it's value from the output of a command?

.. code-block::

    set !my_variable read message.txt

The `!` tells set to execute the value, and take the result of it as the new value.

Payload unloading
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


Configuration file
------------------

Read the :doc:`configuration`
