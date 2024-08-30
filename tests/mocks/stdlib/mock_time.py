"""
Mock time module
"""

import pytest
import pytest_mock

@pytest.fixture
def mock_sleep(mocker: pytest_mock.MockerFixture):
    return mocker.patch("time.sleep")


@pytest.fixture
def mock_sleep_interrupt(mocker: pytest_mock.MockerFixture):
    return mocker.patch("time.sleep", side_effect=KeyboardInterrupt)
