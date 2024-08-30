"""
Mock program_wrapper module
"""

import pytest
import pytest_mock

import snr.core.util.program_wrapper

BLOCK_LIST1 = """
{
    "blockdevices":
    [
        {
            "name": "sda",
            "uuid": null,
            "type": "disk",
            "size": 256060514304,
            "path": "/dev/sda",
            "children": [
                {
                    "name": "sda1",
                    "uuid": "1234-5678",
                    "type": "part",
                    "size": 536870912,
                    "path": "/dev/sda1"
                },
                {
                    "name": "sda2",
                    "uuid": "12345678-1234-1234-1234-1234567890AB",
                    "type": "part",
                    "size": 255522242560,
                    "path": "/dev/sda2"
                }
            ]
        },
        {
            "name": "sdb",
            "uuid": null,
            "type": "disk",
            "size": 256060514304,
            "path": "/dev/sdb",
            "children": [
                {
                    "name": "sdb1",
                    "uuid": "8765-4321",
                    "type": "part",
                    "size": 536870912,
                    "path": "/dev/sdb1"
                },
                {
                    "name": "sdb2",
                    "uuid": "BA0987654321-4321-4321-4321-87654321",
                    "type": "part",
                    "size": 255522242560,
                    "path": "/dev/sdb2"
                },
                {
                    "name": "sdb3",
                    "uuid": "BA0987654322-4321-4321-4321-87654321",
                    "type": "crypt",
                    "size": 255522242560,
                    "path": "/dev/sdb3"
                }
            ]
        }
    ]
}
"""

MOUNT_MOUNTS_DEVICE = "/dev/sda1"
MOUNT_MOUNTS_ALT_DEVICE = "/dev/nvme0n1"
MOUNT_MOUNTS_MOUNT_POINT = "/"
MOUNT_MOUNTS_ALT_MOUNT_POINT = "/alt"
MOUNT_MOUNTS = f"{MOUNT_MOUNTS_DEVICE} on " + \
    f"{MOUNT_MOUNTS_MOUNT_POINT} type ext4\n"
MOUNT_ALT_MOUNTS = f"{MOUNT_MOUNTS_ALT_DEVICE} on " + \
    f"{MOUNT_MOUNTS_ALT_MOUNT_POINT} type ext4\n"
ALL_MOUNTS = f"{MOUNT_MOUNTS}{MOUNT_ALT_MOUNTS}"


@pytest.fixture
def mock_mount_list_mounts(mocker: pytest_mock.MockerFixture):
    mount = mocker.patch("snr.core.util.programs.Mount",
                         spec=snr.core.util.program_wrapper.ProgramWrapperBase)
    mount.return_value.stdout.read.return_value = ALL_MOUNTS
    mount.return_value.invoke_and_wait.return_value = 0
    return mount


@pytest.fixture
def mock_mount_dumb(mocker: pytest_mock.MockerFixture):
    return mocker.patch("snr.core.util.programs.Mount",
                        spec=snr.core.util.program_wrapper.ProgramWrapperBase)


@pytest.fixture
def mock_mount_success(mocker: pytest_mock.MockerFixture):
    mount = mocker.patch("snr.core.util.programs.Mount",
                         spec=snr.core.util.program_wrapper.ProgramWrapperBase)
    mount.return_value.invoke_and_wait.return_value = 0
    return mount


@pytest.fixture
def mock_mount_error(mocker: pytest_mock.MockerFixture):
    mount = mocker.patch("snr.core.util.programs.Mount",
                         spec=snr.core.util.program_wrapper.ProgramWrapperBase)
    mount.return_value.invoke_and_wait.return_value = 1
    return mount


@pytest.fixture
def mock_umount_dumb(mocker: pytest_mock.MockerFixture):
    return mocker.patch("snr.core.util.programs.Umount",
                        spec=snr.core.util.program_wrapper.ProgramWrapperBase)


@pytest.fixture
def mock_lsblk_block_list1(mocker: pytest_mock.MockerFixture):
    lsblk = mocker.patch("snr.core.util.programs.Lsblk",
                         spec=snr.core.util.program_wrapper.ProgramWrapperBase)
    lsblk.return_value.stdout.read.return_value = BLOCK_LIST1
    return lsblk


@pytest.fixture
def mock_vgscan_dumb(mocker: pytest_mock.MockerFixture):
    return mocker.patch("snr.core.util.programs.Vgscan",
                        spec=snr.core.util.program_wrapper.ProgramWrapperBase)


@pytest.fixture
def mock_lvscan_dumb(mocker: pytest_mock.MockerFixture):
    return mocker.patch("snr.core.util.programs.Lvscan",
                        spec=snr.core.util.program_wrapper.ProgramWrapperBase)


@pytest.fixture
def mock_pvchange_dumb(mocker: pytest_mock.MockerFixture):
    return mocker.patch("snr.core.util.programs.Pvchange",
                        spec=snr.core.util.program_wrapper.ProgramWrapperBase)


@pytest.fixture
def mock_cryptsetup_dumb(mocker: pytest_mock.MockerFixture):
    return mocker.patch("snr.core.util.programs.Cryptsetup",
                        spec=snr.core.util.program_wrapper.ProgramWrapperBase)


@pytest.fixture
def mock_cryptsetup_success(mocker: pytest_mock.MockerFixture):
    mock = mocker.patch("snr.core.util.programs.Cryptsetup",
                        spec=snr.core.util.program_wrapper.ProgramWrapperBase)
    mock.invoke_and_wait.return_value = 0
    return mock


@pytest.fixture
def mock_cryptsetup_error(mocker: pytest_mock.MockerFixture):
    mock = mocker.patch("snr.core.util.programs.Cryptsetup",
                        spec=snr.core.util.program_wrapper.ProgramWrapperBase)
    mock.invoke_and_wait.return_value = 1
    return mock
