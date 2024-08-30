"""
Mock safety_pin module
"""

import pytest
import pytest_mock


@pytest.fixture
def mock_check_lack_of_safety_pin_true(mocker: pytest_mock.MockerFixture):
    return mocker.patch("snr.core.payload.safety_pin.check_lack_of_safety_pin", return_value=True)


@pytest.fixture
def mock_check_lack_of_safety_pin_false(mocker: pytest_mock.MockerFixture):
    return mocker.patch("snr.core.payload.safety_pin.check_lack_of_safety_pin", return_value=False)


@pytest.fixture
def mock_remove_safety_pin_success(mocker: pytest_mock.MockerFixture):
    return mocker.patch("snr.core.payload.safety_pin.remove_safety_pin")


@pytest.fixture
def mock_remove_safety_pin_permission_error(mocker: pytest_mock.MockerFixture):
    return mocker.patch("snr.core.payload.safety_pin.remove_safety_pin", side_effect=PermissionError)


@pytest.fixture
def mock_require_lack_of_safety_pin_success(mocker: pytest_mock.MockerFixture):
    return mocker.patch("snr.core.payload.safety_pin.require_lack_of_safety_pin")


@pytest.fixture
def mock_require_lack_of_safety_pin_error(mocker: pytest_mock.MockerFixture):
    return mocker.patch("snr.core.payload.safety_pin.require_lack_of_safety_pin", side_effect=SystemExit)


@pytest.fixture
def mock_module_core_payload_safety_pin(mock_check_lack_of_safety_pin_true, mock_remove_safety_pin_success, mock_require_lack_of_safety_pin_success):
    pass
