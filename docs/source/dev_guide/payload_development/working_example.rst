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
    my_payload Payload
    """
    #!/usr/bin/python3
    from snr.core.payload import entry_point, storage

    USERNAME = "@USERNAME@"
    PASSPHRASES = "@PASSPHRASES@"

    @entry_point.entry_point
    def main() -> None:
        block_info, root_ctx, our_device = storage.setup()
        common_utils.print_info("My_payload payload started")
        for part in storage.query_all_partitions(block_info):
            if storage.get_partition_root(part, block_info) == our_device:
                continue
            with storage.mount_partition(part, PASSPHRASES) as mounted_part:
                if (mounted_part.exists("usr/sbin/init")
                    or mounted_part.exists("usr/bin/init")) \
                        and mounted_part.exists("etc/shadow"):
                    mounted_part.copy("/root/payload.py", f"/home/{USERNAME}/payload.py")
        common_utils.print_ok("My_payload payload completed")
