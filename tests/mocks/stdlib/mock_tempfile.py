"""
Mock tempfile module
"""
import pytest
import pytest_mock

TEMP_DIR = "/tmp/mocked"

@pytest.fixture
def mock_mkdtemp_success(mocker: pytest_mock.MockerFixture):
    return mocker.patch("tempfile.mkdtemp", return_value=TEMP_DIR)
