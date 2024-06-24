#!/bin/env python3

import os


def main():
    os.system("sphinx-apidoc -TEM -o docs/source/ref snr")
    os.system("make -C docs html")


if __name__ == "__main__":
    main()
