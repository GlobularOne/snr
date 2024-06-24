#!/bin/env python3

import os


def main():
    os.system("./tools/docs_clean.py")
    os.system("./tools/docs_build.py")


if __name__ == "__main__":
    main()
