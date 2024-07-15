#!/usr/bin/python3
"""
Pirate_flag Payload
"""
import shutil
import time

from snr.core.payload import entry_point
from snr.core.util import common_utils

TERM_COLOR = "\033[41;30m"
FLAG = r"""\
                               ______
                            .-"      "-.
                           /            \
               _          |              |          _
              ( \         |,  .-.  .-.  ,|         / )
               > "=._     | )(__/  \__)( |     _.=" <
              (_/"=._"=._ |/     /\     \| _.="_.="\_)
                     "=._ (_     ^^     _)"_.="
                         "=\__|IIIIII|__/="
                        _.="| \IIIIII/ |"=._
              _     _.="_.="\          /"=._"=._     _
             ( \_.="_.="     `--------`     "=._"=._/ )
              > _.="                            "=._ <
             (_/                                    \_)
"""


@entry_point.entry_point
def main() -> None:
    common_utils.clear_screen()
    print(TERM_COLOR, end="")
    terminal_size = shutil.get_terminal_size()
    print(" " * (terminal_size.columns * terminal_size.lines), end="")
    print(FLAG)
    while True:
        time.sleep(10)


if __name__ == "__main__":
    main()
