import pytest
import pytest_mock

import snr.core.payload.storage

from .mocks.core.payload.mock_storage import *
from .mocks.core.util.mock_common_utils import *
from .mocks.core.util.mock_programs import *
from .mocks.stdlib.mock_builtins import *
from .mocks.stdlib.mock_os import *
from .mocks.stdlib.mock_os_path import *
from .mocks.stdlib.mock_tempfile import *
from .mocks.stdlib.mock_time import *


@pytest.fixture
def mock_efi_part(mock_exists_false, mocker: pytest_mock.MockerFixture):
    def isdir(path: str):
        return path == f"{TEMP_DIR}/EFI"

    def listdir(path: str):
        return ["BOOT"] if path == f"{TEMP_DIR}/EFI" else []
    mocker.patch("os.path.isdir", new=isdir)
    mocker.patch("os.listdir", new=listdir)


@pytest.fixture
def mock_boot_part(mock_listdir_empty, mocker: pytest_mock.MockerFixture):
    def isdir(path: str):
        return path in (f"{TEMP_DIR}/boot", f"{TEMP_DIR}/boot/grub")

    def exists(path: str):
        return path == f"{TEMP_DIR}/boot/vmlinuz"
    mocker.patch("os.path.isdir", new=isdir)
    mocker.patch("os.path.exists", new=exists)


@pytest.fixture
def mock_data_part(mock_exists_false, mock_listdir_empty, mocker: pytest_mock.MockerFixture):
    def isdir(path: str):
        return path in (f"{TEMP_DIR}/boot")
    mocker.patch("os.path.isdir", new=isdir)


@pytest.fixture
def mock_windows_part(mock_exists_false, mock_listdir_empty, mocker: pytest_mock.MockerFixture):
    def isdir(path: str):
        return path == f"{TEMP_DIR}/Windows/System32"
    mocker.patch("os.path.isdir", new=isdir)


@pytest.fixture
def mock_linux_part(mock_isdir_false, mock_listdir_empty, mocker: pytest_mock.MockerFixture):
    def exists(path: str):
        return path in (f"{TEMP_DIR}/etc/os-release", f"{TEMP_DIR}/etc/shadow")
    mocker.patch("os.path.exists", new=exists)


def test_query_all_block_info(mock_lsblk_block_list1):
    block_info = snr.core.payload.storage.query_all_block_info()
    assert len(block_info) == 2
    assert block_info[0].name == "sda"
    assert block_info[0] == "/dev/sda"
    assert block_info[0] != block_info[1]
    with pytest.raises(NotImplementedError):
        assert not (block_info[0] == True)
    assert not block_info[0].is_partition()
    assert block_info[0].is_disk()
    assert not block_info[0].is_crypt()
    assert not block_info[0].is_loop()
    assert not block_info[0].is_rom()


def test_query_all_partitions(mock_root_device, mock_query_all_block_info_list1):
    partitions = snr.core.payload.storage.query_all_partitions()
    snr.core.payload.storage.query_all_partitions(
        mock_query_all_block_info_list1())
    assert len(partitions) == 2
    assert partitions[0] == "/dev/sdb1"


def test_query_partition_info_by_path(mock_query_all_block_info_list1):
    result = snr.core.payload.storage.query_partition_info_by_path("/dev/sda1")
    snr.core.payload.storage.query_partition_info_by_path(
        "/dev/sda1", mock_query_all_block_info_list1())
    assert result is not None
    assert result.name == "sda1"


def test_query_partition_info_by_path_invalid(mock_query_all_block_info_list1):
    result = snr.core.payload.storage.query_partition_info_by_path("/dev/sdX1")
    assert result is None


def test_query_partition_info_by_uuid(mock_query_all_block_info_list1):
    result = snr.core.payload.storage.query_partition_info_by_uuid("1234-5678")
    snr.core.payload.storage.query_partition_info_by_uuid(
        "1234-5678", mock_query_all_block_info_list1())
    assert result is not None
    assert result.name == "sda1"


def test_query_partition_info_by_uuid_invalid(mock_query_all_block_info_list1):
    result = snr.core.payload.storage.query_partition_info_by_uuid("ABCD-EF01")
    assert result is None


def test_query_partition_info_by_name(mock_query_all_block_info_list1):
    result = snr.core.payload.storage.query_partition_info_by_name("sda1")
    snr.core.payload.storage.query_partition_info_by_name(
        "sda1", mock_query_all_block_info_list1())
    assert result is not None
    assert result.path == "/dev/sda1"


def test_query_partition_info_by_name_invalid(mock_query_all_block_info_list1):
    result = snr.core.payload.storage.query_partition_info_by_name("sdX1")
    assert result is None


def test_lvm_scan_all(mock_vgscan_dumb, mock_lvscan_dumb):
    snr.core.payload.storage.lvm_scan_all()
    mock_vgscan_dumb().invoke_and_wait.assert_called_once()
    mock_lvscan_dumb().invoke_and_wait.assert_called_once()


def test_lvm_activate_all_vgs(mock_pvchange_dumb):
    snr.core.payload.storage.lvm_activate_all_vgs()
    mock_pvchange_dumb().invoke_and_wait.assert_called_once()


def test_luks_is_partition_encrypted(mock_cryptsetup_success):
    assert snr.core.payload.storage.luks_is_partition_encrypted(
        "/dev/sda1") is False


def test_luks_open(mock_cryptsetup_success):
    assert snr.core.payload.storage.luks_open(
        "/dev/sda1", "sda1_crypt", "passphrase") is True


def test_luks_close(mock_cryptsetup_success):
    assert snr.core.payload.storage.luks_close("sda1_crypt") is True


def test_get_partition_root(mock_query_all_block_info_list1):
    assert snr.core.payload.storage.get_partition_root(
        "/dev/sda1") == "/dev/sda"
    assert snr.core.payload.storage.get_partition_root(
        "/dev/sda1", mock_query_all_block_info_list1()) == "/dev/sda"


def test_require_root_device(mock_query_all_block_info_list1):
    assert snr.core.payload.storage.require_root_device(
        "/dev/sda1") == "/dev/sda"


def test_require_root_device_exit(mock_query_all_block_info_list1):
    with pytest.raises(SystemExit):
        snr.core.payload.storage.require_root_device("/dev/moz")


def test_setup(mock_mount_list_mounts, mock_require_root_device, mock_lvm_scan_all_success, mock_lvm_activate_all_vgs_success, mock_query_all_block_info_list1):
    block_info, context, root_device = snr.core.payload.storage.setup()
    assert len(block_info) == 2
    assert root_device is not None


def test_setup_no_lvm(mock_mount_list_mounts, mock_require_root_device, mock_lvm_scan_all_success, mock_lvm_activate_all_vgs_success, mock_query_all_block_info_list1):
    block_info, context, root_device = snr.core.payload.storage.setup(
        no_lvm=True)
    assert len(block_info) == 2
    assert root_device is not None


def test_handle_luks_partition_passphrase(mock_print_info, mock_print_warning, mocker):
    def luks_open(part: str, luks_name: str, passphrase: str):
        return passphrase == "test2"
    mock_luks_open = mocker.patch(
        "snr.core.payload.storage.luks_open", new=luks_open)
    result = snr.core.payload.storage.handle_luks_partition(
        "/dev/sda1", ["test", "test2", "test3"])
    assert result == ("sda1_crypt", "/dev/mapper/sda1_crypt")


def test_handle_luks_partition_timeout(mock_print_info, mock_print_warning, mock_sleep, mocker):
    def luks_open(part: str, luks_name: str, passphrase: str):
        return False
    mock_luks_open = mocker.patch(
        "snr.core.payload.storage.luks_open", new=luks_open)
    result = snr.core.payload.storage.handle_luks_partition("/dev/sda1")
    assert result == (None, None)


def test_handle_luks_partition_interactive(mock_print_info, mock_print_warning, mock_sleep_interrupt, mock_input_string, mocker):
    def luks_open(part: str, luks_name: str, passphrase: str):
        return passphrase == INPUT_STRING
    mock_luks_open = mocker.patch(
        "snr.core.payload.storage.luks_open", new=luks_open)
    result = snr.core.payload.storage.handle_luks_partition(
        "/dev/sda1", ["test"])
    assert result == ("sda1_crypt", "/dev/mapper/sda1_crypt")


def test_handle_luks_partition_wrong_passphrase(mock_print_info, mock_print_warning, mock_sleep_interrupt, mock_input_string_then_interrupt, mocker):
    def luks_open(part: str, luks_name: str, passphrase: str):
        return False
    mock_luks_open = mocker.patch(
        "snr.core.payload.storage.luks_open", new=luks_open)
    result = snr.core.payload.storage.handle_luks_partition(
        "/dev/sda1", ["test"])
    assert result == (None, None)


def test_handle_luks_partition_no_passphrase(mock_print_info, mock_print_warning, mock_sleep_interrupt, mock_input_interrupt, mocker):
    def luks_open(part: str, luks_name: str, passphrase: str):
        return passphrase == INPUT_STRING
    mock_luks_open = mocker.patch(
        "snr.core.payload.storage.luks_open", new=luks_open)
    result = snr.core.payload.storage.handle_luks_partition(
        "/dev/sda1", ["test"])
    assert result == (None, None)


def test_mount_partition(mock_mkdtemp_success, mock_mount_success, mock_umount_dumb, mock_luks_is_partition_encrypted_false, mock_handle_luks_partition_success, mock_luks_close_success):
    with snr.core.payload.storage.mount_partition("/dev/sda1") as mounted:
        assert mounted.mount_point is not None

    mock_mount_success().invoke_and_wait.assert_called_once()
    mock_umount_dumb().invoke_and_wait.assert_called_once()
    mock_luks_close_success.assert_not_called()


def test_mount_failure(mock_mkdtemp_success, mock_mount_error, mock_umount_dumb, mock_luks_is_partition_encrypted_false, mock_handle_luks_partition_success, mock_luks_close_success):
    with pytest.raises(RuntimeError):
        with snr.core.payload.storage.mount_partition("/dev/sda1") as mounted:
            pass


def test_mount_partition_unlock_failure(mock_mkdtemp_success, mock_mount_success, mock_umount_dumb, mock_luks_is_partition_encrypted_true, mock_handle_luks_partition_error, mock_luks_close_success):
    with pytest.raises(RuntimeError):
        with snr.core.payload.storage.mount_partition("/dev/sda1") as mounted:
            pass


def test_mount_partition_no_luks(mock_mkdtemp_success, mock_mount_success, mock_umount_dumb, mock_luks_is_partition_encrypted_false, mock_handle_luks_partition_success, mock_luks_close_success):
    with snr.core.payload.storage.mount_partition("/dev/sda1", no_luks=True) as mounted:
        assert mounted.mount_point is not None

    mock_mount_success().invoke_and_wait.assert_called_once()
    mock_umount_dumb().invoke_and_wait.assert_called_once()
    mock_luks_close_success.assert_not_called()


def test_mount_partition_encrypted(mock_mkdtemp_success, mock_mount_success, mock_umount_dumb, mock_luks_is_partition_encrypted_true, mock_handle_luks_partition_success, mock_luks_close_success):
    with snr.core.payload.storage.mount_partition("/dev/sda1") as mounted:
        assert mounted.mount_point is not None

    mock_mount_success().invoke_and_wait.assert_called_once()
    mock_umount_dumb().invoke_and_wait.assert_called_once()
    mock_luks_close_success.assert_called_once()


def test_mount_partition_encrypted_failure(mock_mkdtemp_success, mock_mount_error, mock_umount_dumb, mock_luks_is_partition_encrypted_true, mock_handle_luks_partition_success, mock_luks_close_success):
    with pytest.raises(RuntimeError):
        with snr.core.payload.storage.mount_partition("/dev/sda1") as mounted:
            pass


def test_is_efi(mock_efi_part, mock_mkdtemp_success, mock_mount_success, mock_umount_dumb, mock_luks_is_partition_encrypted_false, mock_handle_luks_partition_success, mock_luks_close_success):
    with snr.core.payload.storage.mount_partition("/dev/sda1") as mounted:
        assert mounted.mount_point is not None
        assert mounted.is_efi() == True
        # To check the cache functionality
        assert mounted.is_efi() == True


def test_is_boot(mock_boot_part, mock_mkdtemp_success, mock_mount_success, mock_umount_dumb, mock_luks_is_partition_encrypted_false, mock_handle_luks_partition_success, mock_luks_close_success):
    with snr.core.payload.storage.mount_partition("/dev/sda1") as mounted:
        assert mounted.mount_point is not None
        assert mounted.is_boot() == True


def test_is_system(mock_linux_part, mock_mkdtemp_success, mock_mount_success, mock_umount_dumb, mock_luks_is_partition_encrypted_false, mock_handle_luks_partition_success, mock_luks_close_success):
    with snr.core.payload.storage.mount_partition("/dev/sda1") as mounted:
        assert mounted.mount_point is not None
        assert mounted.is_system() == True


def test_is_data(mock_data_part, mock_mkdtemp_success, mock_mount_success, mock_umount_dumb, mock_luks_is_partition_encrypted_false, mock_handle_luks_partition_success, mock_luks_close_success):
    with snr.core.payload.storage.mount_partition("/dev/sda1") as mounted:
        assert mounted.mount_point is not None
        assert mounted.is_data() == True


def test_is_linux(mock_linux_part, mock_mkdtemp_success, mock_mount_success, mock_umount_dumb, mock_luks_is_partition_encrypted_false, mock_handle_luks_partition_success, mock_luks_close_success):
    with snr.core.payload.storage.mount_partition("/dev/sda1") as mounted:
        assert mounted.mount_point is not None
        assert mounted.is_linux() == True


def test_is_windows(mock_windows_part, mock_mkdtemp_success, mock_mount_success, mock_umount_dumb, mock_luks_is_partition_encrypted_false, mock_handle_luks_partition_success, mock_luks_close_success):
    with snr.core.payload.storage.mount_partition("/dev/sda1") as mounted:
        assert mounted.mount_point is not None
        assert mounted.is_windows() == True
