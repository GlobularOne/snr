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
python3 -m pipx install snr==1.0.1

echo "Installation successful. Initializing..."

snr --init

