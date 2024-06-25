#!/bin/env python3

import os
import sys


def main():
    errorcode = os.system("./tools/docs_clean.py")
    if errorcode != 0:
        sys.exit(errorcode)
    sys.exit(os.system("./tools/docs_build.py"))


if __name__ == "__main__":
    main()
