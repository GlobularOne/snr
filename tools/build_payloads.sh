#!/bin/bash

set -e

make -C snr/payloads/tampering/disk_encryption
rm -rf snr/payloads/tampering/disk_encryption/{src,Makefile}
