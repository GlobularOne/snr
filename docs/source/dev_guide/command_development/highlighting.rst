Shell highlighting
==================

To add your new command to the syntax highlighting, open up `snr/cli/lexer.py`. Scroll down until you find the `SnrLexer` class and the `tokens` member. 
Add a line for your command in the `commands` list:

.. code-block:: python

    pygments.lexer.include('my_command')

Now, find the command before your command inside your command's category, scroll up a bit until you find `SYNTAX` constant and find it.

Depending on how the user interacts with your command, there are some templates for you on what to add there:

Command accepts no arguments
----------------------------

.. code-block:: python

    **command_no_args("my_command")


Command accepts one or more optional argument
---------------------------------------------

.. code-block:: python

    **command_args("my_command")    


Command accepts one keyword argument
------------------------------------

.. code-block:: python

    **command_key_no_args("my_command", ("keyword1", "keyword2", "keyword3"))

Command accepts one keyword argument and one or more arguments
--------------------------------------------------------------

.. code-block:: python

    **command_key_args("my_command", ("keyword1", "keyword2", "keyword3"))
