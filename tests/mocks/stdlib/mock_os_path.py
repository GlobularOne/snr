"""
Mock os.path module
"""

import pytest
import pytest_mock


@pytest.fixture
def mock_exists_false(mocker: pytest_mock.MockerFixture):
    return mocker.patch("os.path.exists", return_value=False)


@pytest.fixture
def mock_exists_true(mocker: pytest_mock.MockerFixture):
    return mocker.patch("os.path.exists", return_value=True)


@pytest.fixture
def mock_isdir_false(mocker: pytest_mock.MockerFixture):
    return mocker.patch("os.path.exists", return_value=False)


@pytest.fixture
def mock_isdir_true(mocker: pytest_mock.MockerFixture):
    return mocker.patch("os.path.isdir", return_value=True)

@pytest.fixture
def mock_islink_false(mocker: pytest_mock.MockerFixture):
    return mocker.patch("os.path.islink", return_value=False)


@pytest.fixture
def mock_islink_true(mocker: pytest_mock.MockerFixture):
    return mocker.patch("os.path.islink", return_value=True)


@pytest.fixture
def mock_isfile_false(mocker: pytest_mock.MockerFixture):
    return mocker.patch("os.path.isfile", return_value=False)


@pytest.fixture
def mock_isfile_true(mocker: pytest_mock.MockerFixture):
    return mocker.patch("os.path.isfile", return_value=True)
