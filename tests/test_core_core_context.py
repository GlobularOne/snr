import pytest

import snr.core.core.context


def test_context_initialization():
    device_name = "/dev/sda"
    context = snr.core.core.context.Context(device_name)

    assert context.device_name == device_name
    assert context.original_target == device_name
    assert context.level == 0


def test_to_level_1():
    context = snr.core.core.context.Context("/dev/sda")
    context.to_level_1(device_size=1024, is_device=True)

    assert context.level == 1
    assert context.device_size == 1024
    assert context.is_device is True


def test_to_level_2():
    context = snr.core.core.context.Context("/dev/sda")
    context.to_level_1(device_size=1024, is_device=True)
    context.to_level_2(partitions_prefix="/dev/sda1")

    assert context.level == 2
    assert context.partitions_prefix == "/dev/sda1"


def test_to_level_3():
    context = snr.core.core.context.Context("/dev/sda")
    context.to_level_1(device_size=1024, is_device=True)
    context.to_level_2(partitions_prefix="/dev/sda1")
    context.to_level_3(root_directory="/mnt/sda")

    assert context.level == 3
    assert context.root_directory == "/mnt/sda"


def test_device_size_access_before_level_1():
    context = snr.core.core.context.Context("/dev/sda")
    with pytest.raises(RuntimeError, match="Context does not yet have device_size"):
        _ = context.device_size


def test_is_device_access_before_level_1():
    context = snr.core.core.context.Context("/dev/sda")
    with pytest.raises(RuntimeError, match="Context does not yet have is_device"):
        _ = context.is_device


def test_partitions_prefix_access_before_level_2():
    context = snr.core.core.context.Context("/dev/sda")
    context.to_level_1(device_size=1024, is_device=True)
    with pytest.raises(RuntimeError, match="Context does not yet have partitions_prefix"):
        _ = context.partitions_prefix


def test_root_directory_access_before_level_3():
    context = snr.core.core.context.Context("/dev/sda")
    context.to_level_1(device_size=1024, is_device=True)
    context.to_level_2(partitions_prefix="/dev/sda1")
    with pytest.raises(RuntimeError, match="Context does not yet have root_directory"):
        _ = context.root_directory


def test_construct_partition_path_with_original_target():
    context = snr.core.core.context.Context("/dev/sda")
    context.to_level_1(device_size=1024, is_device=True)
    context.to_level_2(partitions_prefix="/dev/sda1")
    context.to_level_3(root_directory="/mnt/sda")

    partition_path = context.construct_partition_path(0, original_target=True)
    assert partition_path == "/dev/sda/dev/sda10"


def test_construct_partition_path_without_original_target():
    context = snr.core.core.context.Context("/dev/sda")
    context.to_level_1(device_size=1024, is_device=True)
    context.to_level_2(partitions_prefix="/dev/sda1")
    context.to_level_3(root_directory="/mnt/sda")

    partition_path = context.construct_partition_path(0, original_target=False)
    assert partition_path == "/dev/sda/dev/sda10"
