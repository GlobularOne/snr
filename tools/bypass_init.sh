#!/bin/bash

mkdir -p ~/.local/share/snr/rootfs
mkdir -p ~/.config/snr
mkdir -p ~/.local/state/snr
mkdir -p ~/.cache/snr
tar -caf ~/.local/share/snr/noble-x86_64.tar.gz -C ~/.local/share/snr/rootfs .
echo -n 3 >  ~/.local/share/snr/noble-x86_64.tar.gz.version
