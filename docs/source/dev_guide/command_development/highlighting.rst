Shell Highlighting
==================

To add your new command to the syntax highlighting, open up `snr/cli/lexer.py`. Scroll down until you find the `SnrLexer` class and the `tokens` member. 
Add a line for your command in the `commands` list:

.. code-block:: python

    pygments.lexer.include('my_command')

Now, find the command before yours inside the category, scroll up a bit until you find `SYNTAX` constant.

Depending on how the user interacts with your command, there are some templates for you on what to add there:

Command Accepts No Arguments
----------------------------

.. code-block:: python

    **command_no_args("my_command")


Command Accepts One or More Optional Arguments
----------------------------------------------

.. code-block:: python

    **command_args("my_command")    


Command Accepts One Keyword Argument
------------------------------------

.. code-block:: python

    **command_key_no_args("my_command", ("keyword1", "keyword2", "keyword3"))

Command Accepts One Keyword Argument and One or More Optional Arguments
-----------------------------------------------------------------------

.. code-block:: python

    **command_key_args("my_command", ("keyword1", "keyword2", "keyword3"))

That's all you need to do. You got it!
