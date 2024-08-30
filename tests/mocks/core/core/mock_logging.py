"""
Mock logging module
"""

import pytest
import pytest_mock


@pytest.fixture
def mock_carriage_return(mocker: pytest_mock.MockerFixture):
    return mocker.patch("snr.core.core.logging.carriage_return")


@pytest.fixture
def mock_clear_screen(mocker: pytest_mock.MockerFixture):
    return mocker.patch("snr.core.core.logging.clear_screen")


@pytest.fixture
def mock_print_sys(mocker: pytest_mock.MockerFixture):
    return mocker.patch("snr.core.core.logging.print_sys")


@pytest.fixture
def mock_print_debug(mocker: pytest_mock.MockerFixture):
    return mocker.patch("snr.core.core.logging.print_debug")


@pytest.fixture
def mock_print_info(mocker: pytest_mock.MockerFixture):
    return mocker.patch("snr.core.core.logging.print_info")


@pytest.fixture
def mock_print_ok(mocker: pytest_mock.MockerFixture):
    return mocker.patch("snr.core.core.logging.print_ok")


@pytest.fixture
def mock_print_warning(mocker: pytest_mock.MockerFixture):
    return mocker.patch("snr.core.core.logging.print_warning")


@pytest.fixture
def mock_print_error(mocker: pytest_mock.MockerFixture):
    return mocker.patch("snr.core.core.logging.print_error")


@pytest.fixture
def mock_print_fatal(mocker: pytest_mock.MockerFixture):
    return mocker.patch("snr.core.core.logging.print_fatal")


@pytest.fixture
def mock_module_core_core_logging(mock_carriage_return, mock_clear_screen, mock_print_sys,
                                  mock_print_debug, mock_print_info, mock_print_ok,
                                  mock_print_warning, mock_print_error, mock_print_fatal):
    pass
