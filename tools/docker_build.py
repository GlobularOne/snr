#!/bin/env python3

import os
import sys


def main():
    sys.exit(os.system("docker build -t globularone/snr ."))


if __name__ == "__main__":
    main()
