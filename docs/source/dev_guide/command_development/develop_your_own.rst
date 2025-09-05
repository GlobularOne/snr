Develop Your Own Command
========================

.. note:: Snr is written majorly in python, this guide assumes you already have a basic understanding of it. If not, you can check out many Python tutorials or courses first.

While snr does not provide a method to hot plug a module and load a command, it does not mean you can't add a custom command to snr. To do so you need to do a few things:

* Identify the group the command belongs to (either of `filesystem`, `misc`, `payload` or `variable`.)
* Add the function of the command.
* Document it (In `docs/user_guide/shell_commands.rst` as well.)
* Provide necessary information for the syntax highlighting (read :doc:`highlighting`.)

Basics of Commands
------------------

Each command is simply a function (prefixed by `cmd_`) inside the categories that are in `snr/cli/commands`. The documentation of these commands is the function's docstring.
The basic command would be:

.. code-block:: python

    @interactive_shell.interactive_shell.command(name="my_command")
    def cmd_my_command() -> str | None:
        return "my_command has been invoked"

The function decorator adds it to the commands, the `name` parameter being the command name. Then, as you can see, the return value of the command is not what it prints (those are just logs.)
but the value it returns. This allows the shell to process the output if it needs to before printing it back to the user (this makes things like `set !my_var my_command` possible.)

Add an Argument
---------------

Let's add a basic argument:

.. code-block:: python

    @interactive_shell.interactive_shell.command(name="my_command")
    @click.argument("argument")
    def cmd_my_command(argument: str) -> str | None:
        return f"my_command has been invoked with '{argument}'"


Add an Optional Argument
------------------------

.. code-block:: python

    @interactive_shell.interactive_shell.command(name="my_command")
    @click.argument("argument", required=False)
    def cmd_my_command(argument: str) -> str | None:
        if len(argument) == 0:
            return f"my_command has been invoked with nothing" 
        return f"my_command has been invoked with '{argument}'"

Add an Integer Argument
-----------------------

.. code-block:: python

    @interactive_shell.interactive_shell.command(name="my_command")
    @click.argument("argument", type=int)
    def cmd_my_command(argument: int) -> str | None:
        return f"my_command has been invoked with '{argument}'"


Add a Path Argument
-------------------

.. code-block:: python

    @interactive_shell.interactive_shell.command(name="my_command")
    @click.argument("path", type=click.Path())
    def cmd_my_command(path: str) -> str | None:
        return f"my_command has been invoked with path '{argument}'"

Control what kind of path is ok using the follow parameters to `click.Path`:

* exists: The path must exist.
* file_okay: The path can be a file.
* dir_okay: The path can be a directory.
* readable: The path must be readable.
* writable: The path must be writable.
* executable: The path must be executable.


That's all you need to know!

.. seealso::

    :doc:`highlighting`
        To make the syntax highlighting also recognize your command.
