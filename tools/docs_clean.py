#!/bin/env python3

import shutil
import os


def main():
    if os.path.exists("docs/build"):
        shutil.rmtree("docs/build")
    if os.path.exists("docs/source/ref"):
        shutil.rmtree("docs/source/ref")


if __name__ == "__main__":
    main()
