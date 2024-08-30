import struct
import sys

import pytest

from .mocks import hivex
from .mocks.core.core.mock_path_wrapper import *
from .mocks.hivex import HIVEX_DECODED_VALUES, hive_types, mock_Hivex

sys.modules["hivex"] = hivex
sys.modules["hivex.hive_types"] = hive_types
import snr.core.payload.nt_registry


def test_registry_node_value_init(mock_Hivex):
    registry_value = snr.core.payload.nt_registry.RegistryNodeValue(
        mock_Hivex, 1, "Key1")

    assert registry_value.key == "Key1"
    assert registry_value.value == b"MockValue"
    assert registry_value.type == hive_types.REG_BINARY


def test_registry_node_value_init(mock_Hivex):
    registry_value = snr.core.payload.nt_registry.RegistryNodeValue(
        mock_Hivex, 1, "Key534", (hive_types.REG_BINARY, b"1"))


@pytest.mark.parametrize("value,t,raw_value,should_fail",
                         (
                             (b"MOZ!\x00", hive_types.REG_QWORD, "", True),
                             (12, 23312, "", True),
                             (b"NewValue", hive_types.REG_BINARY, b"NewValue", False),
                             (12, hive_types.REG_DWORD,
                              struct.pack("<I", 12), False),
                             (12, hive_types.REG_DWORD_BIG_ENDIAN,
                              struct.pack(">I", 12), False),
                             ("Moz!", hive_types.REG_EXPAND_SZ, b"Moz!\x00", False),
                             ("Moz!", hive_types.REG_LINK, b"Moz!\x00", False),
                             (["Moz!", "Double Moz!"], hive_types.REG_MULTI_SZ,
                              b"Moz!\x00Double Moz!\x00\x00", False),
                             (b"NewValue", hive_types.REG_NONE, b"NewValue", False),
                             (0xFFFFFFFFFF, hive_types.REG_QWORD,
                              struct.pack("<q", 0xFFFFFFFFFF), False),
                             ("Moz!", hive_types.REG_SZ, b"Moz!\x00", False),
                             (b"Moz!\x00", 12463, b"Moz!\x00", False),
                         ))
def test_registry_node_value_sync(value, t, raw_value, should_fail, mock_Hivex):
    registry_value = snr.core.payload.nt_registry.RegistryNodeValue(
        mock_Hivex, 1, "Key1")

    registry_value._type = t
    if should_fail:
        with pytest.raises(TypeError):
            registry_value.value = value
        return
    else:
        registry_value.value = value

    mock_Hivex.node_set_value.assert_called_with(1, {
        "key": "Key1",
        "t": t,
        "value": raw_value
    })


@pytest.mark.parametrize("handle,value", HIVEX_DECODED_VALUES)
def test_registry_node_init(handle, value, mock_Hivex):
    registry_node = snr.core.payload.nt_registry.RegistryNode(mock_Hivex, 1)
    print(registry_node.data[f"Key{handle}"].key)
    print(registry_node.data[f"Key{handle}"].type)
    assert registry_node.data[f"Key{handle}"].value == value
    assert registry_node.name == "MockNode"
    assert registry_node.timestamp == 1234567890
    assert registry_node.parent is None
    assert "Key1" in registry_node.data
    assert "Key2" in registry_node.data


def test_registry_value_as_bytes(mock_Hivex):
    registry_node = snr.core.payload.nt_registry.RegistryNode(mock_Hivex, 1)
    assert registry_node.data["Key1"].value_as_bytes(
    ) == HIVEX_DECODED_VALUES[0][1]


def test_registry_value_as_bytes_error(mock_Hivex):
    registry_node = snr.core.payload.nt_registry.RegistryNode(mock_Hivex, 1)
    with pytest.raises(TypeError):
        registry_node.data["Key2"].value_as_bytes()


def test_registry_value_as_string(mock_Hivex):
    registry_node = snr.core.payload.nt_registry.RegistryNode(mock_Hivex, 1)
    assert registry_node.data["Key4"].value_as_string(
    ) == HIVEX_DECODED_VALUES[3][1]


def test_registry_value_as_string_error(mock_Hivex):
    registry_node = snr.core.payload.nt_registry.RegistryNode(mock_Hivex, 1)
    with pytest.raises(TypeError):
        registry_node.data["Key1"].value_as_string()


def test_registry_value_as_int(mock_Hivex):
    registry_node = snr.core.payload.nt_registry.RegistryNode(mock_Hivex, 1)
    assert registry_node.data["Key2"].value_as_int(
    ) == HIVEX_DECODED_VALUES[1][1]


def test_registry_value_as_int_error(mock_Hivex):
    registry_node = snr.core.payload.nt_registry.RegistryNode(mock_Hivex, 1)
    with pytest.raises(TypeError):
        registry_node.data["Key1"].value_as_int()


def test_registry_value_as_list(mock_Hivex):
    registry_node = snr.core.payload.nt_registry.RegistryNode(mock_Hivex, 1)
    assert registry_node.data["Key6"].value_as_list(
    ) == HIVEX_DECODED_VALUES[5][1]


def test_registry_value_as_list_error(mock_Hivex):
    registry_node = snr.core.payload.nt_registry.RegistryNode(mock_Hivex, 1)
    with pytest.raises(TypeError):
        registry_node.data["Key1"].value_as_list()


def test_registry_node_get_children_count(mock_Hivex):
    mock_Hivex.node_nr_children.return_value = 2
    registry_node = snr.core.payload.nt_registry.RegistryNode(mock_Hivex, 1)
    assert registry_node.get_children_count() == 2


def test_registry_node_new_child(mock_Hivex):
    snr.core.payload.nt_registry.RegistryNode(mock_Hivex, 1).new_child("Moz")


def test_registry_node_del_child(mock_Hivex):
    snr.core.payload.nt_registry.RegistryNode(mock_Hivex, 1).del_child(
        snr.core.payload.nt_registry.RegistryNode(mock_Hivex, 2))


def test_registry_node_new_data(mock_Hivex):
    snr.core.payload.nt_registry.RegistryNode(
        mock_Hivex, 1).new_data("Key543", hive_types.REG_BINARY, b"1")


def test_registry_node_get_children(mock_Hivex):
    registry_node = snr.core.payload.nt_registry.RegistryNode(mock_Hivex, 1)
    for child in registry_node.get_children():
        assert isinstance(child, snr.core.payload.nt_registry.RegistryNode)


def test_nt_registry_find_node_absolute(mock_Hivex, mock_PathWrapperBase_everything_works):
    nt_registry = snr.core.payload.nt_registry.NtRegistry(
        mock_PathWrapperBase_everything_works)
    node = nt_registry.find_node("HKLM\\SOFTWARE")
    node = nt_registry.find_node("HKLM\\SOFTWARE")
    assert node is not None


def test_nt_registry_find_bad_hive(mock_Hivex, mock_PathWrapperBase_everything_works):
    mock_PathWrapperBase_everything_works.exists = lambda x: False
    nt_registry = snr.core.payload.nt_registry.NtRegistry(
        mock_PathWrapperBase_everything_works)
    with pytest.raises(FileNotFoundError):
        nt_registry.find_node("HKLM\\SOFTWARE")


def test_nt_registry_find_node_relative(mock_Hivex, mock_PathWrapperBase_everything_works):
    nt_registry = snr.core.payload.nt_registry.NtRegistry(
        mock_PathWrapperBase_everything_works)
    root_node = nt_registry.find_node("HKLM\\SOFTWARE")
    node = nt_registry.find_node("\\some\\path", root_node)
    assert node is not None


def test_nt_registry_find_node_invalid_path(mock_Hivex, mock_PathWrapperBase_everything_works):
    nt_registry = snr.core.payload.nt_registry.NtRegistry(
        mock_PathWrapperBase_everything_works)
    with pytest.raises(ValueError):
        nt_registry.find_node("HKLM\\InvalidHive")


def test_nt_registry_find_node_bad_relative(mock_Hivex, mock_PathWrapperBase_everything_works):
    nt_registry = snr.core.payload.nt_registry.NtRegistry(
        mock_PathWrapperBase_everything_works)
    with pytest.raises(ValueError):
        nt_registry.find_node("\\InvalidHive")


def test_nt_registry_find_node_bad_format(mock_Hivex, mock_PathWrapperBase_everything_works):
    nt_registry = snr.core.payload.nt_registry.NtRegistry(
        mock_PathWrapperBase_everything_works)
    with pytest.raises(ValueError):
        nt_registry.find_node("/InvalidHive")


def test_nt_registry_find_node_non_existent(mock_Hivex, mock_PathWrapperBase_everything_works,
                                            mocker):
    nt_registry = snr.core.payload.nt_registry.NtRegistry(
        mock_PathWrapperBase_everything_works)
    root_node = nt_registry.find_node("HKLM\\SOFTWARE")
    nt_registry._hives["SOFTWARE"].node_get_child.return_value = None
    node = nt_registry.find_node("\\some\\path", root_node)
    assert node is None


def test_nt_registry_exit(mock_Hivex, mock_PathWrapperBase_everything_works):
    with snr.core.payload.nt_registry.NtRegistry(mock_PathWrapperBase_everything_works) as nt_registry:
        nt_registry.find_node("HKLM\\SYSTEM\\test")
        hive = nt_registry._hives["SYSTEM"]
    hive.commit.assert_called_once()
