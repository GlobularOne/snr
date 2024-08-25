"""
Change registry on the device. Add registries like this:

set HKLM\\Whatever\\Whatever2 key:type:value

To set the default key, value for a registry. Use the defacto standard of @ for key:

set HKLM\\Whatever\\Whatever @:type:value

Valid types are:

    REG_BINARY, REG_NONE: Enter as hex value (e.g 00 01 02)
    REG_DWORD, REG_DWORD_BIG_ENDIAN, REG_QWORD: Enter as integer (e.g 127)
    REG_EXPAND_SZ, REG_LINK, REG_SZ: Enter as string (e.g my value)

The payload will automatically search for variables that start with HKLM or HKEY_LOCAL_MACHINE and process them.
"""
from snr.core.payload.payload import Context, Payload
from snr.core.util import common_utils
from snr.cli import variables


class RegistryPayload(Payload):
    AUTHORS = ("GlobularOne",)
    TARGET_OS_LIST = ("Microsoft Windows",)
    INPUTS = (
        Payload.supports_encrypted_access()
    )
    VALID_REG_TYPEs: dict[str, type[bytes | int | str]] = {
        "REG_BINARY": bytes,
        "REG_NONE": bytes,
        "REG_DWORD": int,
        "REG_DWORD_BIG_ENDIAN": int,
        "REG_QWORD": int,
        "REG_EXPAND_SZ": str,
        "REG_LINK": str,
        "REG_SZ": str,
    }

    def generate(self, ctx: Context) -> int:
        registries: dict[str, bytes | int | str] = {}
        our_vars = {}
        for name in variables.global_vars.get_variables_name():
            if name.startswith(("HKLM", "HKEY_LOCAL_MACHINE")):
                # Both are common mistakes we can deal with
                name = name.replace("\\\\", "\\").replace("/", "\\")
                # While they are technically correct in syntax, it will break our payload
                name = name.replace("HKLM:", "HKLM\\").replace("HKEY_LOCAL_MACHINE:", "HKEY_LOCAL_MACHINE\\")
                # Now that we know this variable is intended for us, we can try to validate it
                try:
                    key, type_, value = variables.global_vars.get_variable_str(
                        name).split(":", maxsplit=2)
                except ValueError:
                    common_utils.print_error(
                        f"Invalid syntax for value of {name}, it must be in format key:type:value")
                    return 1
                except TypeError:
                    common_utils.print_error(
                        f"Invalid type for variable {name}. The variable must be a string")
                    return 1
                if len(key) == 0:
                    common_utils.print_error(
                        f"Invalid key for {name}. For default value use @ instead of an empty key")
                    return 1
                type_ = type_.upper()
                if type_ not in self.VALID_REG_TYPEs:
                    common_utils.print_error(
                        f"Invalid type for {name}. Use `info` to see more about valid types")
                    return 1
                # Interpret and validate the value
                new_value: bytes | int | str
                match type_:
                    case "REG_BINARY" | "REG_NONE":
                        # Value is a sequence of hex bytes separated by spaces
                        new_value = b""
                        for byte in value.split(" "):
                            try:
                                new_value += bytes(int(byte, base=16))
                            except ValueError:
                                common_utils.print_error(
                                    f"Invalid value for {name}. '{byte}' is not a valid hexadecimal number")
                                return 1

                    case "REG_DWORD" | "REG_DWORD_BIG_ENDIAN" | "REG_QWORD":
                        # Value is a number
                        try:
                            new_value = int(value)
                        except ValueError:
                            common_utils.print_error(
                                f"Invalid value for {name}. '{value}' is not a valid hexadecimal number")
                            return 1
                        # We don't concern ourselves with the integer size, that's not our issue
                    case "REG_EXPAND_SZ" | "REG_LINK" | "REG_SZ":
                        new_value = value
            registries[name + f":{key}:{type_}"] = new_value
        our_vars["REGISTRIES"] = registries
        self.format_payload_and_write(ctx, our_vars)
        self.add_autorun(ctx)
        return 0


payload = RegistryPayload()
