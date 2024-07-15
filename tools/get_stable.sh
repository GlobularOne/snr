#!/bin/bash

set -e

get_distribution() {
    if [ -r /etc/os-release ]; then
        . /etc/os-release
        if [ -n "$ID" ]; then
            echo "$ID"
            return
        fi
    fi
    echo "unknown"
}

nonroot_init_workaround() {
    ORIG_CWD=$(pwd)
    USER=$(id -un)
    cd ~
    sudo HOME=$(pwd) snr --init --init-only
    sudo chown $USER:$USER -R ~/.local/share/snr ~/.local/state/snr ~/.config/snr ~/.cache/snr
    sudo tar -C ~/.local/share/snr/rootfs -xf ~/.local/share/snr/jammy-x86_64.tar.gz
    sudo rm -f ~/.local/share/snr/rootfs/jammy-x86_64.tar.gz
    sudo chown $USER:$USER -R ~/.local/share/snr/rootfs
    tar -C ~/.local/share/snr/rootfs -caf ~/.local/share/snr/jammy-x86_64.tar.gz 
    cd $ORIG_CWD
}

DISTRO=$(get_distribution)

echo "Installing pipx"
python3 -m pip install --user pipx
python3 -m pipx ensurepath

echo "Installing snr runtime dependencies"

case "$DISTRO" in
    debian|ubuntu|kali|parrot)
        sudo apt update
        sudo apt install fakeroot fakechroot debootstrap
        ;;
    fedora)
        sudo dnf install fakeroot fakechroot debootstrap
        ;;
    arch)
        sudo pacman -S fakeroot fakechroot debootstrap 
        ;;
    *)
        echo "Unsupported distribution: $DISTRO"
        exit 1
        ;;
esac


echo "Installing snr"
python3 -m pipx install snr==1.1.0

echo "Installation successful. Initializing..."

if [[ $(id -u ) == 0 ]]; then
    snr --init --init-only
else
    nonroot_init_workaround
fi
