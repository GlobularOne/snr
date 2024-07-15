"""
Use multiple payloads. To use:
  1. Set variable `PAYLOADS` to all the payloads you want (for example: set PAYLOADS extraction/install_account_hashes;infection/meterpreter)
  2. Load the payload (use misc/multi)
  3. Set all the variables the payloads you selected need
  4. Use generate normally

Note that loading misc/multi and then setting PAYLOADS does not do anything. It should be done BEFORE loading the payload.
"""
from snr.cli import variables
from snr.core.payload.payload import Context, Payload
from snr.core.payload_generation import generation


class MultiPayload(Payload):
    AUTHORS = ("GlobularOne",)
    TARGET_OS_LIST = ("Any",)

    _payloads: list[Payload]
    _payload_names: list[str]

    def load(self) -> int:
        payloads: list[str] = []
        self._payloads = []
        if variables.global_vars.get_variable_info("PAYLOADS").var_type == str:
            # We haven't been loaded before
            payloads.extend(variables.global_vars.get_variable_str(
                "PAYLOADS").split(";"))
        else:
            # We have been loaded before
            payloads.extend(
                variables.global_vars.get_variable_list("PAYLOADS"))
        variables.global_vars.del_variable("PAYLOADS")
        # For many reasons, including ensuring the user doesn't end up deleting this variable
        self.INPUTS = ((
            "PAYLOADS", payloads, -1, "Payloads to load. Not effective after loading the payload"
        ),)
        self._payload_names = payloads
        # Now, load the payloads
        for path in payloads:
            payload_instance = generation.load(path)
            if payload_instance is None:
                return 1
            self._payloads.append(
                payload_instance)  # pylint: disable=no-member
        errorcode = super().load()
        if errorcode != 0:
            self.unload()
            return errorcode
        return 0

    def generate(self, ctx: Context) -> int:
        for i, p in enumerate(self._payloads):
            if not generation.generate(self._payload_names[i], p, ctx):
                self.unload()
                return 1
        return 0

    def unload(self) -> int:
        # While it's true that most payloads don't even have a custom unload method
        # and use the default one which does absolutely nothing. We never know, one may do.
        for i, p in enumerate(self._payloads):
            generation.unload(self._payload_names[i], p)
        return 0


payload = MultiPayload()
