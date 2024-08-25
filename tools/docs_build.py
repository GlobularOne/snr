#!/bin/env python3

import os
import sys

def main():
    errorcode = os.system("sphinx-apidoc -TMe -o docs/source/ref snr")
    if errorcode != 0:
        sys.exit(errorcode)
    sys.exit(os.system("make -C docs html"))


if __name__ == "__main__":
    main()
