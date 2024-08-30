"""
Mock shutil module
"""

import pytest
import pytest_mock


@pytest.fixture
def mock_copy_success(mocker: pytest_mock.MockerFixture):
    return mocker.patch("shutil.copy")


@pytest.fixture
def mock_copyfile_success(mocker: pytest_mock.MockerFixture):
    return mocker.patch("shutil.copyfile")


@pytest.fixture
def mock_copytree_success(mocker: pytest_mock.MockerFixture):
    return mocker.patch("shutil.copytree")


@pytest.fixture
def mock_rmtree_success(mocker: pytest_mock.MockerFixture):
    return mocker.patch("shutil.rmtree")
