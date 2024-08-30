"""
Mock context module
"""

import pytest
import pytest_mock

import snr.core.core.context

from ..core.mock_path_wrapper import mock_PathWrapperBase_everything_works

CONTEXT_DEVICE_NAME = "/dev/sdb1"
CONTEXT_DEVICE_SIZE = 0
CONTEXT_IS_DEVICE = True
CONTEXT_PARTITIONS_PREFIX = ""
CONTEXT_MOUNT_POINT = "/"


@pytest.fixture
def mock_create_context_for_mount_point_valid(mocker: pytest_mock.MockerFixture):
    context = snr.core.core.context.Context(CONTEXT_DEVICE_NAME)
    context.to_level_1(CONTEXT_DEVICE_SIZE, CONTEXT_IS_DEVICE)
    context.to_level_2(CONTEXT_PARTITIONS_PREFIX)
    context.to_level_3(CONTEXT_MOUNT_POINT)
    return mocker.patch("snr.core.payload.context.create_context_for_mount_point", return_value=context)


@pytest.fixture
def mock_create_context_for_mount_point_invalid(mocker: pytest_mock.MockerFixture):
    return mocker.patch("snr.core.payload.context.create_context_for_mount_point", return_value=None)


@pytest.fixture
def mock_module_core_payload_context(mock_create_context_for_mount_point_valid, mock_PathWrapperBase_everything_works):
    pass
