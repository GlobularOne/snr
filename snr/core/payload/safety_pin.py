"""
Library support for the safety pin. The safety pin is a feature on all payloads.
It checks whatever the payload is installed or not and if not running from a target, it won't run.
All the payloads that come with snr do use the safety pin.
For custom written payloads, you must use the entry_point function decorator
"""
import os.path

__all__ = (
    "check_lack_of_safety_pin", "remove_safety_pin",
    "require_lack_of_safety_pin"
)


def check_lack_of_safety_pin() -> bool:
    """Check if the safety pin is lacking

    Returns:
        True, if there is a problem False
    """
    return os.path.exists("/root/.give_em_hell")


def remove_safety_pin(root: str) -> None:
    """Remove the safety pin

    Args:
        root: path to root of the filesystem to remove it's safety pin
    """
    with open(os.path.join(root, "root", ".give_em_hell"), "w", encoding="utf-8") as stream:
        stream.write("Safety Pin")


def require_lack_of_safety_pin() -> None:
    """Check if we lack the safety pin. If the safety pin exists, exit the program

    Raises:
        SystemExit: If safety pin exists
    """
    if not check_lack_of_safety_pin():
        raise SystemExit(1)
