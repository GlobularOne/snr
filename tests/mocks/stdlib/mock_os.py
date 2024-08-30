"""
Mock os module
"""

import pytest
import pytest_mock

LISTDIR_EMPTY = []
LISTDIR_FILES = ["file1.txt", "file2.txt"]
LISTDIR_DIRS = ["dir1", "dir2"]
LISTDIR_ALL = [*LISTDIR_FILES, *LISTDIR_DIRS]


@pytest.fixture
def mock_link_success(mocker: pytest_mock.MockerFixture):
    return mocker.patch("os.link")


@pytest.fixture
def mock_link_existing_dest(mocker: pytest_mock.MockerFixture):
    return mocker.patch("os.link", side_effect=FileExistsError)


@pytest.fixture
def mock_link_permission_error(mocker: pytest_mock.MockerFixture):
    return mocker.patch("os.link", side_effect=PermissionError)


@pytest.fixture
def mock_link_non_existent(mocker: pytest_mock.MockerFixture):
    return mocker.patch("os.link", side_effect=FileNotFoundError)


@pytest.fixture
def mock_mkdir_success(mocker: pytest_mock.MockerFixture):
    return mocker.patch("os.mkdir", return_value=False)


@pytest.fixture
def mock_mkdir_error(mocker: pytest_mock.MockerFixture):
    return mocker.patch("os.mkdir", side_effect=PermissionError)


@pytest.fixture
def mock_makedirs_success(mocker: pytest_mock.MockerFixture):
    return mocker.patch("os.makedirs", return_value=False)


@pytest.fixture
def mock_makedirs_error(mocker: pytest_mock.MockerFixture):
    return mocker.patch("os.makedirs", side_effect=PermissionError)


@pytest.fixture
def mock_listdir_empty(mocker: pytest_mock.MockerFixture):
    return mocker.patch("os.listdir", return_value=LISTDIR_EMPTY)


@pytest.fixture
def mock_listdir_files(mocker: pytest_mock.MockerFixture):
    return mocker.patch("os.listdir", return_value=LISTDIR_FILES)


@pytest.fixture
def mock_listdir_dirs(mocker: pytest_mock.MockerFixture):
    return mocker.patch("os.listdir", return_value=LISTDIR_DIRS)


@pytest.fixture
def mock_listdir_all(mocker: pytest_mock.MockerFixture):
    return mocker.patch("os.listdir", return_value=LISTDIR_ALL)


@pytest.fixture
def mock_rmdir_success(mocker: pytest_mock.MockerFixture):
    return mocker.patch("os.rmdir")


@pytest.fixture
def mock_rmdir_error(mocker: pytest_mock.MockerFixture):
    return mocker.patch("os.rmdir", side_effect=PermissionError)


@pytest.fixture
def mock_rmdir_error_non_empty(mocker: pytest_mock.MockerFixture):
    return mocker.patch("os.rmdir", side_effect=OSError)


@pytest.fixture
def mock_remove_success(mocker: pytest_mock.MockerFixture):
    return mocker.patch("os.remove")
