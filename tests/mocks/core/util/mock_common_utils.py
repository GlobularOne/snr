"""
Mock common_utils module
"""
import pytest
import pytest_mock


@pytest.fixture
def mock_handle_exception(mocker: pytest_mock.MockerFixture):
    return mocker.patch("snr.core.util.common_utils.handle_exception")


@pytest.fixture
def mock_carriage_return(mocker: pytest_mock.MockerFixture):
    return mocker.patch("snr.core.util.common_utils.carriage_return")


@pytest.fixture
def mock_clear_screen(mocker: pytest_mock.MockerFixture):
    return mocker.patch("snr.core.util.common_utils.clear_screen")


@pytest.fixture
def mock_print_sys(mocker: pytest_mock.MockerFixture):
    return mocker.patch("snr.core.util.common_utils.print_sys")


@pytest.fixture
def mock_print_debug(mocker: pytest_mock.MockerFixture):
    return mocker.patch("snr.core.util.common_utils.print_debug")


@pytest.fixture
def mock_print_info(mocker: pytest_mock.MockerFixture):
    return mocker.patch("snr.core.util.common_utils.print_info")


@pytest.fixture
def mock_print_ok(mocker: pytest_mock.MockerFixture):
    return mocker.patch("snr.core.util.common_utils.print_ok")


@pytest.fixture
def mock_print_warning(mocker: pytest_mock.MockerFixture):
    return mocker.patch("snr.core.util.common_utils.print_warning")


@pytest.fixture
def mock_print_error(mocker: pytest_mock.MockerFixture):
    return mocker.patch("snr.core.util.common_utils.print_error")


@pytest.fixture
def mock_print_fatal(mocker: pytest_mock.MockerFixture):
    return mocker.patch("snr.core.util.common_utils.print_fatal")
