"""
Mock variables module
"""
import pytest
import pytest_mock


@pytest.fixture
def mock_global_vars(mocker: pytest_mock.MockerFixture):
    return mocker.patch('snr.cli.variables.global_vars')
