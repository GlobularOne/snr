import struct

import pytest
import pytest_mock

from .hive_types import *

HIVEX_VALUES = (
    (REG_BINARY, b"MockValue"),
    (REG_DWORD, struct.pack("<I", 12)),
    (REG_DWORD_BIG_ENDIAN, struct.pack(">I", 12)),
    (REG_EXPAND_SZ, b"Moz!\x00"),
    (REG_LINK, b"Moz!\x00"),
    (REG_MULTI_SZ, b"Moz!\x00Double Moz!\x00\x00"),
    (REG_MULTI_SZ, b"\x00"),
    (REG_NONE, b"NewValue"),
    (REG_QWORD, struct.pack("<q", 0xFFFFFFFFFF)),
    (REG_SZ, b"Moz!\x00"),
    (12463, b"Moz!\x00"),
)

HIVEX_DECODED_VALUES = (
    (1, b"MockValue"),
    (2, 12),
    (3, 12),
    (4, "Moz!"),
    (5, "Moz!"),
    (6, ["Moz!", "Double Moz!"]),
    (7, []),
    (8, b"NewValue"),
    (9, 0xFFFFFFFFFF),
    (10, "Moz!"),
    (11, b"Moz!\x00"),
)


class Hivex:
    pass


@pytest.fixture
def mock_Hivex(mocker: pytest_mock.MockerFixture):
    def new_hivex():
        hivex = mocker.MagicMock()
        hivex.node_name.return_value = "MockNode"
        hivex.node_timestamp.return_value = 1234567890
        hivex.node_parent.side_effect = RuntimeError
        hivex.node_values.return_value = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        hivex.node_get_value.side_effect = lambda _, x: int(x.strip("Key"))
        hivex.node_children.return_value = [1]
        hivex.node_add_child.side_effect = lambda _, __: 1
        hivex.value_key.side_effect = lambda x: f"Key{x}"
        hivex.value_value.side_effect = lambda x: HIVEX_VALUES[x-1]
        return hivex
    return mocker.patch("hivex.Hivex", new_callable=new_hivex)
