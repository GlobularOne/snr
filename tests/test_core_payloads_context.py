import pytest

import snr.core.payload.context

from .mocks.core.util.mock_programs import *


def test_create_context_for_mount_point_success(mock_mount_list_mounts):
    context = snr.core.payload.context.create_context_for_mount_point(
        MOUNT_MOUNTS_MOUNT_POINT)
    assert isinstance(context, snr.core.payload.context.Context)
    assert context.device_name == MOUNT_MOUNTS_DEVICE
    assert context.level == 3
    assert context.root_directory == MOUNT_MOUNTS_MOUNT_POINT
    context = snr.core.payload.context.create_context_for_mount_point(
        MOUNT_MOUNTS_ALT_MOUNT_POINT)
    assert isinstance(context, snr.core.payload.context.Context)
    assert context.device_name == MOUNT_MOUNTS_ALT_DEVICE
    assert context.level == 3
    assert context.root_directory == MOUNT_MOUNTS_ALT_MOUNT_POINT


def test_create_context_for_mount_point_invalid(mock_mount_list_mounts):
    invalid_mount_point = "/invalid/mount_point"
    with pytest.raises(ValueError, match=f"'{invalid_mount_point}' is not a valid mount point"):
        snr.core.payload.context.create_context_for_mount_point(
            invalid_mount_point)


def test_require_context_for_mount_point_success(mock_mount_list_mounts):
    context = snr.core.payload.context.require_context_for_mount_point(
        MOUNT_MOUNTS_MOUNT_POINT)
    assert isinstance(context, snr.core.payload.context.Context)
    assert context.device_name == MOUNT_MOUNTS_DEVICE
    assert context.level == 3
    assert context.root_directory == MOUNT_MOUNTS_MOUNT_POINT


def test_require_context_for_mount_point_invalid(mock_mount_list_mounts):
    with pytest.raises(SystemExit):
        snr.core.payload.context.require_context_for_mount_point(
            "/invalid/mount_point")
