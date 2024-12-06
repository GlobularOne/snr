#!/bin/bash

mkdir -p ${XDG_DATA_HOME:-~/.local/share}/snr/rootfs
mkdir -p ${XDG_CONFIG_HOME:-~/.config}/.config/snr
mkdir -p ${XDG_DATA_HOME:-~/.local/state}/snr
mkdir -p ${XDG_CACHE_HOME:-~/.cache}/snr
tar -caf ${XDG_DATA_HOME:-~/.local/share}/snr/noble-x86_64.tar.gz -C ${XDG_DATA_HOME:-~/.local/share}/snr/rootfs .
echo -n 3 > ${XDG_DATA_HOME:-~/.local/share}/snr/noble-x86_64.tar.gz.version
