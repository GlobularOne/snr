"""
Edit NT registry values
"""
import contextlib
import struct
from typing import Any, Generator

import hivex
import hivex.hive_types
from hivex.hive_types import (REG_BINARY, REG_DWORD, REG_DWORD_BIG_ENDIAN,
                              REG_EXPAND_SZ, REG_LINK, REG_MULTI_SZ, REG_NONE,
                              REG_QWORD, REG_SZ)

from snr.core.core import path_wrapper

__all__ = (
    "REG_BINARY", "REG_DWORD", "REG_DWORD_BIG_ENDIAN",
    "REG_EXPAND_SZ", "REG_LINK", "REG_MULTI_SZ",
    "REG_NONE", "REG_QWORD", "REG_SZ",
    "RegistryNodeValue", "RegistryNode", "NtRegistry",
)

# Mapping of registry types to python types
REG_TYPE_MAPPING: dict[int, type[bytes | int | str | list]] = {
    REG_BINARY: bytes,
    REG_DWORD: int,
    REG_DWORD_BIG_ENDIAN: int,
    REG_EXPAND_SZ: str,
    REG_LINK: str,
    REG_MULTI_SZ: list,
    REG_NONE: bytes,
    REG_QWORD: int,
    REG_SZ: str,
}


class RegistryNodeValue:
    """
    A value of a node in a registry
    """
    _hive: hivex.Hivex
    _node_handle: int
    _key: str
    _value: bytes | int | str | list[str]
    _type: int

    def __init__(self, hive: hivex.Hivex, node_handle: int, key: str, type_value: tuple[int, bytes | int | str | list[str] | None] = (REG_NONE, None)):
        self._hive = hive
        self._node_handle = node_handle
        self._key = key
        if type_value[1] is None:
            self._type, value = self._hive.value_value(
                self._hive.node_get_value(self._node_handle, self.key))
        else:
            self._type, value = type_value
        # Try to interpret the value
        match self._type:
            case hivex.hive_types.REG_BINARY:
                self._value = value
            case hivex.hive_types.REG_DWORD:
                self._value = struct.unpack("<I", value)[0]
            case hivex.hive_types.REG_DWORD_BIG_ENDIAN:
                self._value = struct.unpack(">I", value)[0]
            case hivex.hive_types.REG_EXPAND_SZ:
                self._value = value.decode()
            case hivex.hive_types.REG_LINK:
                self._value = value.decode()
            case hivex.hive_types.REG_MULTI_SZ:
                self._value = []
                values = value.split(b"\x00")
                if len(values) > 2:
                    # By definition the sequence comes with it's own null terminator
                    for i in range(len(values) - 2):
                        self._value.append(values[i].decode())
            case hivex.hive_types.REG_NONE:
                # We can't guess the type, so we don't process it
                self._value = value
            case hivex.hive_types.REG_QWORD:
                self._value = struct.unpack("<Q", value)[0]
            case hivex.hive_types.REG_SZ:
                self._value = value.decode()
            case _:
                # We don't know it
                self._value = value
        if type_value[1] is None:
            self.sync()

    def sync(self):
        """
        Synchronize our information with the registry, note that this doesn't change it on the disk.
        You generally don't need to worry about this and just change the value.
        """
        packed_value: bytes
        match self._type:
            case hivex.hive_types.REG_BINARY:
                assert isinstance(self._value, bytes)
                packed_value = self._value
            case hivex.hive_types.REG_DWORD:
                assert isinstance(self._value, int)
                packed_value = struct.pack("<I", self._value)
            case hivex.hive_types.REG_DWORD_BIG_ENDIAN:
                assert isinstance(self._value, int)
                packed_value = struct.pack(">I", self._value)
            case hivex.hive_types.REG_EXPAND_SZ:
                assert isinstance(self._value, str)
                packed_value = self._value.encode() + b"\x00"
            case hivex.hive_types.REG_LINK:
                assert isinstance(self._value, str)
                packed_value = self._value.encode() + b"\x00"
            case hivex.hive_types.REG_MULTI_SZ:
                assert isinstance(self._value, list)
                packed_value = b""
                for value in self._value:
                    assert isinstance(value, str)
                    packed_value += value.encode() + b"\x00"
                packed_value += b"\x00"

            case hivex.hive_types.REG_NONE:
                assert isinstance(self._value, bytes)
                # We didn't process it when loading, we won't process it while dumping neither
                packed_value = self._value
            case hivex.hive_types.REG_QWORD:
                assert isinstance(self._value, int)
                packed_value = struct.pack("<Q", self._value)
            case hivex.hive_types.REG_SZ:
                assert isinstance(self._value, str)
                packed_value = self._value.encode() + b"\x00"
            case _:
                assert isinstance(self._value, bytes)
                packed_value = self._value
        self._hive.node_set_value(self._node_handle, {
            "key": self._key,
            "t": self._type,
            "value": packed_value
        })

    @property
    def key(self) -> str:
        """Key of the value
        """
        return self._key

    @property
    def value(self) -> bytes | int | str | list[str]:
        """Registry value
        """
        return self._value

    @value.setter
    def value(self, new_value:  bytes | int | str | list[str]):
        if self._type not in REG_TYPE_MAPPING:
            if not isinstance(new_value, bytes):
                raise TypeError(
                    "Unknown type registry value must be of type bytes")
        elif not isinstance(new_value, REG_TYPE_MAPPING[self._type]):
            raise TypeError(
                f"Value must of type: {REG_TYPE_MAPPING[self._type].__name__}")
        self._value = new_value
        self.sync()

    @property
    def type(self) -> int:
        """Type of the registry value
        """
        return self._type

    def value_as_bytes(self) -> bytes:
        """Return value interpreting it as bytes

        Raises:
            TypeError: Value is not meant to be interpreted as bytes
        """
        if REG_TYPE_MAPPING[self._type] != bytes:
            raise TypeError("Value cannot be interpreted as bytes")
        assert isinstance(self._value, bytes)
        return self._value

    def value_as_string(self) -> str:
        """Return value interpreting it as a string

        Raises:
            TypeError: Value is not meant to be interpreted as a string
        """
        if REG_TYPE_MAPPING[self._type] != str:
            raise TypeError("Value cannot be interpreted as a string")
        assert isinstance(self._value, str)
        return self._value

    def value_as_int(self) -> int:
        """Return value interpreting it as an integer

        Raises:
            TypeError: Value is not meant to be interpreted as an integer
        """
        if REG_TYPE_MAPPING[self._type] != int:
            raise TypeError("Value cannot be interpreted as an integer")
        assert isinstance(self._value, int)
        return self._value

    def value_as_list(self) -> list[str]:
        """Return value interpreting it as a list of strings

        Raises:
            TypeError: Value is not meant to be interpreted as a list of strings
        """
        if REG_TYPE_MAPPING[self._type] != list:
            raise TypeError("Value cannot be interpreted as a list of strings")
        assert isinstance(self._value, list)
        return self._value


class RegistryNode:
    """A registry node

    Attributes:
        handle: Handle of the node
        name: Name of the node
        Timestamp: Last modification timestamp
        parent: Parent node of this node or none if it's the root node
        data: Key and values assigned to this node
    """
    _hive: hivex.Hivex
    handle: int
    name: str
    timestamp: int
    parent: 'RegistryNode' | None
    data: dict[str, RegistryNodeValue]

    def __init__(self, hive: hivex.Hivex, handle: int):
        self._hive = hive
        self.handle = handle
        # Query info
        self.name = self._hive.node_name(self.handle)
        self.timestamp = self._hive.node_timestamp(self.handle)
        try:
            self.parent = self._hive.node_parent(self.handle)
        except RuntimeError:
            # No parent, we are the root
            self.parent = None
        for data_handle in self._hive.node_values(self.handle):
            key = self._hive.value_key(data_handle)
            self.data[key] = RegistryNodeValue(self._hive, self.handle, key)
        self._hive.node_set_value()

    def get_children_count(self) -> int:
        """Get count of children this node has

        Returns:
            Count of children of the current node
        """
        return self._hive.node_nr_children(self.handle)

    def get_children(self) -> Generator['RegistryNode', None, None]:
        """Get children of this node

        Yields:
            Child of this node
        """
        for i in self._hive.node_children(self.handle):
            yield RegistryNode(self._hive, i)

    def find_child(self, key: str) -> 'RegistryNode' | None:
        """Find a child by it's name

        Args:
            key: Name of the child

        Returns:
            The node if found, none otherwise
        """
        return self._hive.node_get_child(self.handle, key)

    def new_child(self, name: str) -> 'RegistryNode':
        """Create a new child node and return it
        """
        return RegistryNode(self._hive, self._hive.node_add_child(self.handle, name))

    def del_child(self, node: 'RegistryNode'):
        """

        Args:
            node: Node to delete
        """
        self._hive.node_delete_child(node.handle)

    def new_data(self, key: str, type_: int, value: bytes | int | str | list[str]) -> RegistryNodeValue:
        """Create a new key, data pair and return it

        Args:
            key: Key for the value
            type_: Type fo the value
            value: Note that value must be compatible with the type

        Returns:
            The registry node value
        """
        return RegistryNodeValue(self._hive, self.handle, key, (type_, value))


class NtRegistry(contextlib.AbstractContextManager['NtRegistry']):
    """
    Manager registry hives
    """
    _hives: dict[str, hivex.Hivex]
    _path_wrapper: path_wrapper.PathWrapperBase

    def __init__(self, wrapper: path_wrapper.PathWrapperBase):
        self._hives = {}
        self._path_wrapper = wrapper

    def __enter__(self) -> 'NtRegistry':
        return self

    def __exit__(self, *_: Any) -> None:
        # To exit, commit all hives and close them
        for hive_name, hive in self._hives.values():
            hive.commit(f"Windows/System32/config/{hive_name}")
            del self._hives[hive_name]

    def find_node(self, path: str, root_node: RegistryNode | None = None) -> RegistryNode | None:
        """Find a node

        There are a few possible valid syntax for path here:
            (HKLM|HKEY_LOCAL_MACHINE)\\whatever
            (HKLM|HKEY_LOCAL_MACHINE):\\whatever
            \\whatever
        The first two do not need a root_node, we are going to find it ourselves (they are absolute)
        The third syntax is a relative search and root_node cannot be None.

        Args:
            path: Path to the node to find
            root_node: Root node to start search from, only used for relative searches. Defaults to None.

        Raises:
            ValueError: If we cannot find the hive or requesting a relative search without a root_node
            FileNotFoundError: We do know the hive but can't find it

        Returns:
            The node found or None if not found
        """
        if path.startswith(("HKLM", "HKEY_LOCAL_MACHINE")):
            # Absolute path
            path = path.removeprefix("HKLM").removeprefix("HKEY_LOCAL_MACHINE")
            path = path.removeprefix("\\").removeprefix(":")
            hive_name = path.split("\\")[0].upper()
            if hive_name not in ("SOFTWARE", "SECURITY", "SYSTEM", "SAM"):
                # we don't know that
                raise ValueError(f"Unknown hive '{hive_name}'")
            # First check if already have opened it
            if hive_name in self._hives:
                hive = self._hives[hive_name]
            else:
                # We have not opened this hive yet, do so
                hive_path = f"Windows/System32/config/{hive_name}"
                if not self._path_wrapper.exists(hive_path):
                    raise FileNotFoundError(
                        f"File '{self._path_wrapper.join(hive_path)}' not found")
                hive = hivex.Hivex(hive_path, write=True)
                self._hives[hive_name] = hive
            root_node = RegistryNode(hive, hive.root())
            # Make the path relative
            path = path.removeprefix(path.split("\\")[0])
        elif path.startswith("\\"):
            if root_node is None:
                raise ValueError(
                    "Cannot do a relative search without a root node")
        else:
            raise ValueError("Path is of unknown format")
        # Make the path suitable for search
        path = path.removeprefix("\\")
        parent_node = root_node
        for node_name in path.split("\\"):
            new_node = parent_node.find_child(node_name)
            if new_node is None:
                return None
            parent_node = new_node
        return parent_node
