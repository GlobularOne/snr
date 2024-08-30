import pytest
import pytest_mock

import snr.core.payload.data_dir
import snr.core.payload.storage
import snr.core.util.programs

from .mocks.core.util.mock_programs import *
from .mocks.stdlib.mock_os import *


@pytest.fixture
def mock_data_directory(mocker: pytest_mock.MockerFixture, mock_rmdir_success, mock_mount_dumb):
    return mock_rmdir_success, mock_mount_dumb


def test_fix_data_dir_writable(mocker, mock_mkdir_success, mock_data_directory):
    snr.core.payload.data_dir.fix_data_dir()
    assert not snr.core.util.programs.Mount().invoke_and_wait.called


def test_fix_data_dir_not_writable(mocker, mock_mkdir_error, mock_data_directory):
    snr.core.payload.data_dir.fix_data_dir()
    snr.core.util.programs.Mount().invoke_and_wait.assert_called_once_with(
        None, "tmpfs", "/data", options={"t": "tmpfs"})


def test_wrap_data_path_for_block(mock_data_directory, mock_mkdir_success, mock_makedirs_success):
    block_info = snr.core.payload.storage.BlockInfo(
        'test', "1234-5678-90AB-CDEF", "part", 1024, "/block/sda1")

    wrapped_path = snr.core.payload.data_dir.wrap_data_path_for_block(
        block_info)
    mock_makedirs_success.assert_called_once_with(
        "/data/1234-5678-90AB-CDEF", mode=511, exist_ok=True)
    assert wrapped_path._path == snr.core.payload.data_dir.data.wrap(
        "1234-5678-90AB-CDEF")._path


def test_wrap_data_path_for_block_no_uuid(mock_data_directory,  mock_mkdir_success, mock_makedirs_success):
    """Test wrap_data_path_for_block function when UUID is None."""
    block_info = snr.core.payload.storage.BlockInfo(
        'test', None, 'loop', 1024, "/dev/loop0")

    wrapped_path = snr.core.payload.data_dir.wrap_data_path_for_block(
        block_info)
    mock_makedirs_success.assert_called_once_with(
        "/data/dev.loop0", mode=511, exist_ok=True)
    assert wrapped_path._path == snr.core.payload.data_dir.data.wrap(
        "dev.loop0")._path
