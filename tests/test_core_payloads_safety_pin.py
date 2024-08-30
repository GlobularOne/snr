import os

import pytest

import snr.core.payload.safety_pin

from .mocks.core.payload.mock_safety_pin import *
from .mocks.stdlib.mock_builtins import *
from .mocks.stdlib.mock_os_path import *


def test_check_lack_of_safety_pin_exists(mock_exists_true):
    assert snr.core.payload.safety_pin.check_lack_of_safety_pin() is True


def test_check_lack_of_safety_pin_not_exists(mock_exists_false):
    assert snr.core.payload.safety_pin.check_lack_of_safety_pin() is False


def test_remove_safety_pin(mock_open):
    root_path = "/mnt"
    snr.core.payload.safety_pin.remove_safety_pin(root_path)
    mock_open.assert_called_once_with(os.path.join(
        root_path, "root", ".give_em_hell"), "w", encoding="utf-8")
    # Check if write was called with the correct content
    mock_open().write.assert_called_once_with("Safety Pin")


def test_require_lack_of_safety_pin_exit(mock_check_lack_of_safety_pin_false):
    with pytest.raises(SystemExit):
        snr.core.payload.safety_pin.require_lack_of_safety_pin()


def test_require_lack_of_safety_pin_no_exit(mock_check_lack_of_safety_pin_true):
    snr.core.payload.safety_pin.require_lack_of_safety_pin()
