"""
Mock storage module
"""
import json

import pytest
import pytest_mock

import snr.core.payload.context
import snr.core.payload.storage

from ..util.mock_programs import *
from .mock_context import *


@pytest.fixture
def mock_query_all_block_info_list1(mocker: pytest_mock.MockerFixture, mock_lsblk_block_list1):
    block_data = json.loads(BLOCK_LIST1)
    block_info = [
        snr.core.payload.storage.BlockInfo(
            block_data["blockdevices"][0]["name"],
            block_data["blockdevices"][0]["uuid"],
            block_data["blockdevices"][0]["type"],
            block_data["blockdevices"][0]["size"],
            block_data["blockdevices"][0]["path"],
            tuple(block_data["blockdevices"][0]["children"])
        ),
        snr.core.payload.storage.BlockInfo(
            block_data["blockdevices"][1]["name"],
            block_data["blockdevices"][1]["uuid"],
            block_data["blockdevices"][1]["type"],
            block_data["blockdevices"][1]["size"],
            block_data["blockdevices"][1]["path"],
            tuple(block_data["blockdevices"][1]["children"])
        )
    ]
    return mocker.patch("snr.core.payload.storage.query_all_block_info", return_value=block_info)


@pytest.fixture
def mock_lvm_scan_all_success(mocker: pytest_mock.MockerFixture):
    return mocker.patch("snr.core.payload.storage.lvm_scan_all")


@pytest.fixture
def mock_lvm_activate_all_vgs_success(mocker: pytest_mock.MockerFixture):
    return mocker.patch("snr.core.payload.storage.lvm_activate_all_vgs")


@pytest.fixture
def mock_luks_is_partition_encrypted_true(mocker: pytest_mock.MockerFixture):
    return mocker.patch("snr.core.payload.storage.luks_is_partition_encrypted", return_value=True)


@pytest.fixture
def mock_luks_is_partition_encrypted_false(mocker: pytest_mock.MockerFixture):
    return mocker.patch("snr.core.payload.storage.luks_is_partition_encrypted", return_value=False)


@pytest.fixture
def mock_luks_close_success(mocker: pytest_mock.MockerFixture):
    return mocker.patch("snr.core.payload.storage.luks_close", return_value=True)


@pytest.fixture
def mock_require_root_device(mocker: pytest_mock.MockerFixture):
    return mocker.patch("snr.core.payload.storage.require_root_device", return_value="/dev/sda")


@pytest.fixture
def mock_setup_list1(mocker: pytest_mock.MockerFixture):
    block_info = [
    ]
    context = snr.core.core.context.Context(CONTEXT_DEVICE_NAME)
    context.to_level_1(CONTEXT_DEVICE_SIZE,
                       CONTEXT_IS_DEVICE)
    context.to_level_2(CONTEXT_PARTITIONS_PREFIX)
    context.to_level_3(CONTEXT_MOUNT_POINT)
    return mocker.patch("snr.core.payload.storage.setup", return_value=(block_info, context, "/"))


@pytest.fixture
def mock_handle_luks_partition_success(mocker: pytest_mock.MockerFixture):
    return mocker.patch("snr.core.payload.storage.handle_luks_partition",
                        return_value=("/dev/sda1_crypt", "sda1_crypt"))


@pytest.fixture
def mock_handle_luks_partition_error(mocker: pytest_mock.MockerFixture):
    return mocker.patch("snr.core.payload.storage.handle_luks_partition",
                        return_value=(None, None))


@pytest.fixture
def mock_root_device(mocker: pytest_mock.MockerFixture):
    return mocker.patch.object(snr.core.payload.storage, attribute="_root_device", new="/dev/sda")
