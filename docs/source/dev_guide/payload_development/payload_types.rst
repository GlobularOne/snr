Payload Types
=============

The payload itself, can be any file, so you can just download or build an executable and use autorun to run it (See :doc:`/ref/snr.core.payload.payload`.)
Snr also offers a whole range of utilities specifically designed for the payload itself (given you want to use write the payload in python.)
You can see them inside :doc:`/ref/snr.core.payload`. Which are categorized into two:

Standalone Payloads
-------------------

If the payload is not a python file you control, and it just needs to be run. All you need to do is use two utility functions within the Payload class itself (Here we are inside the `generate()` function):

.. warning::
    Standalone payloads are not using a Payload Entry Point, therefore do not initialize the framework and are needless to say not able to use features like safety pin or the `/data` directory.
    We strongly recommend you avoid creating standalone payloads, and instead wrap the payload with a basic Payload Entry Point that just executes the payload.

.. code-block:: python

    self.copy_root_to_root(
            ctx, __file__, "payload", "root/payload")
    self.add_autorun(ctx, "root/payload")

The code above copies a payload file named `payload` inside your payload's package and adds an autorun entry for it.

Here is a basic template:

.. code-block:: python

    """
    Payload description
    """
    from snr.core.payload.payload import Context, Payload


    class MyPayload(Payload):
        ...

        def generate(self, ctx: Context) -> int:
            self.copy_root_to_root(
                ctx, __file__, "payload", "root/payload")
            self.add_autorun(ctx, "root/payload")
            return 0

    payload = MyPayload()


That's it, nothing more is needed. For a full example, you can see the source code to `misc/pirate_flag`.

Framework Payloads
------------------

For these payloads, you can take advantage of the vast number of utilities snr offers for payloads with just simply importing them, here is a basic template:

.. code-block:: python

    """
    Payload description
    """
    from snr.core.payload.payload import Context, Payload


    class MyPayload(Payload):
        ...

        def generate(self, ctx: Context) -> int:
            variables = self.get_self_variables()
            self.format_payload_and_write(ctx, variables)
            self.add_autorun(ctx)
            return 0

    payload = MyPayload()

The generate function here uses three utility functions:

* `get_self_variables`: Returns a dictionary of all the variables you declared in `INPUT`.
* `format_payload_and_write`: Formats a python file using the `AtFormatter` (See :doc:`/ref/snr.core.util.at_formatter`) named `payload.py` copies onto the host filesystem as `/root/payload.py`.
* `add_autorun`: Adds an autorun for `/root/payload.py`. You can override the executable with passing its name.

I highly advise you check out :doc:`/ref/snr.core.payload.payload` to understand these functions better and how to customize them.

For a full example, you can check out the source code of `tampering/disk_encryption`.
