"""
Utilities to deal with Network Interfaces
"""

import socket
import psutil
import psutil._common


class NetworkInterface:
    """A network interface

    Attributes:
        name: Name of the interface
        ipv4_address: IPv4 address of the interface, if IPv4-enabled
        ipv4_broadcast: IPv4 broadcast address of the interface, if IPv4-enabled
        ipv4_netmask: IPv4 network mask of the interface, if IPv4-enabled
        ipv6_address: IPv6 address of the interface, if IPv6-enabled
        ipv6_broadcast: IPv6 broadcast address of the interface, if IPv6-enabled
        ipv6_netmask: IPv6 network mask of the interface, if IPv6-enabled
        mac_address: MAC address of the interface, if a physical network interface
        is_up: Whatever the interface is up or not
        mtu: MTU of the interface
        flags: Flags of the interface (e.g up, broadcast, etc)
    """
    name: str
    ipv4_address: str | None = None
    ipv4_broadcast: str | None = None
    ipv4_netmask: str | None = None
    ipv6_address: str | None = None
    ipv6_broadcast: str | None = None
    ipv6_netmask: str | None = None
    mac_address: str | None = None
    is_up: bool = False
    mtu: int = 0
    flags: tuple[str, ...] = ()

    def __init__(self, name: str, addr_list: list[psutil._common.snicaddr], stat: psutil._common.snicstats):
        self.name = name
        for addr in addr_list:
            match addr.family:
                case socket.AddressFamily.AF_INET:
                    self.ipv4_address = addr.address
                    self.ipv4_broadcast = addr.broadcast
                    self.ipv4_netmask = addr.netmask
                case socket.AddressFamily.AF_INET6:
                    self.ipv6_address = addr.address
                    self.ipv6_broadcast = addr.broadcast
                    self.ipv6_netmask = addr.netmask
                case socket.AddressFamily.AF_PACKET:
                    self.mac_address = addr.address
        self.is_up = stat.isup
        self.mtu = stat.mtu
        self.flags = stat.flags.split(",")


def list_network_interfaces() -> list[NetworkInterface]:
    """Return a list of all network interfaces installed on the machine

    Returns:
        List of all network interfaces installed on the machine
    """
    addrs = psutil.net_if_addrs()
    stats = psutil.net_if_stats()
    ifs = []
    for if_name in addrs:
        ifs.append(NetworkInterface(if_name, addrs[if_name], stats[if_name]))
    return ifs


def get_network_interface(if_name: str) -> NetworkInterface | None:
    """Get a network interface by it's name

    Args:
        if_name: Name of the interface

    Returns:
        Network interface if found, otherwise None 
    """
    addrs = psutil.net_if_addrs()
    stats = psutil.net_if_stats()
    if if_name in addrs and if_name in stats:
        return NetworkInterface(if_name, addrs[if_name], stats[if_name])
    return None
