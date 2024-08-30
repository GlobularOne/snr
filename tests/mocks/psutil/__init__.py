"""
Mock psutil module
"""
import copy
import socket

import psutil
import psutil._common
import pytest
import pytest_mock

NET_ADDRS_LIST1 = {
    # Local Address, has all capabilities
    "lo": [
        psutil._common.snicaddr(
            socket.AddressFamily.AF_INET, "127.0.0.1", "255.0.0.0", None, None),
        psutil._common.snicaddr(socket.AddressFamily.AF_INET6, "::1",
                                "ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff", None, None),
        psutil._common.snicaddr(
            socket.AddressFamily.AF_PACKET, "00:00:00:00:00:00", None, None, None)
    ],
    # Wired connection, no IP capability at all
    "eth0": [
        psutil._common.snicaddr(socket.AddressFamily.AF_PACKET,
                                "01:01:01:01:01:01", None, "ff:ff:ff:ff:ff:ff:ff", None)
    ],
    # Wireless connection, both IPv4 and IPv6
    "wlan0": [
        psutil._common.snicaddr(
            socket.AddressFamily.AF_INET, "192.168.1.2", "255.255.255.0", None, None),
        psutil._common.snicaddr(socket.AddressFamily.AF_INET6,
                                "fd00::1", "ffff:ffff:ffff:ffff::", "ff02::1", None),
        psutil._common.snicaddr(socket.AddressFamily.AF_PACKET,
                                "02:02:02:02:02:02", None, "ff:ff:ff:ff:ff:ff:ff", None)
    ],
    # Tunnel, no IPv6 or PACKET
    "tun0": [
        psutil._common.snicaddr(socket.AddressFamily.AF_INET,
                                "192.168.2.12", "255.255.255.0", None, "192.168.2.1"),
    ]
}

NET_STATS_LIST1 = {
    "lo": psutil._common.snicstats(True, psutil._common.NicDuplex.NIC_DUPLEX_UNKNOWN, 0, 1500, "up,broadcast,multicast"),
    "eth0": psutil._common.snicstats(True, psutil._common.NicDuplex.NIC_DUPLEX_UNKNOWN, 0, 1500, "up,broadcast,multicast"),
    "wlan0": psutil._common.snicstats(True, psutil._common.NicDuplex.NIC_DUPLEX_UNKNOWN, 0, 1500, "up,broadcast,multicast"),
    "tun0": psutil._common.snicstats(True, psutil._common.NicDuplex.NIC_DUPLEX_UNKNOWN, 0, 1500, "up,broadcast,multicast")
}


@pytest.fixture
def mock_net_if_addrs_list1(mocker: pytest_mock.MockerFixture):
    return mocker.patch("psutil.net_if_addrs", return_value=copy.deepcopy(NET_ADDRS_LIST1))


@pytest.fixture
def mock_net_if_stats_list1(mocker: pytest_mock.MockerFixture):
    return mocker.patch("psutil.net_if_stats", return_value=copy.deepcopy(NET_STATS_LIST1))
