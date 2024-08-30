import pytest

import snr.core.core.path_wrapper

from .mocks.stdlib.mock_builtins import *
from .mocks.stdlib.mock_os import *
from .mocks.stdlib.mock_os_path import *
from .mocks.stdlib.mock_shutil import *


@pytest.fixture
def path_wrapper():
    return snr.core.core.path_wrapper.PathWrapperBase("/")


def test_path_wrapper_initialization(path_wrapper):
    assert path_wrapper._path == "/"


def test_join(path_wrapper):
    assert path_wrapper.join("subdir", "file.txt") == "/subdir/file.txt"


def test_exists(path_wrapper, mock_exists_true):
    assert path_wrapper.exists("file.txt") is True


def test_isdir(path_wrapper, mock_isdir_true):
    assert path_wrapper.isdir("subdir") is True


def test_isfile(path_wrapper, mock_isfile_true):
    assert path_wrapper.isfile("file.txt") is True


def test_islink(path_wrapper, mock_islink_false):
    assert path_wrapper.islink("file.txt") is False


def test_open(path_wrapper, mock_open):
    with path_wrapper.open("file.txt", "w") as f:
        f.write("test")
        assert f is not None


def test_remove(path_wrapper, mock_remove_success):
    path_wrapper.remove("file.txt")
    mock_remove_success.assert_called_once_with(path_wrapper.join("file.txt"))


def test_copy(path_wrapper, mock_copy_success):
    path_wrapper.copy("src.txt", "dest.txt")
    mock_copy_success.assert_called_once_with(path_wrapper.join(
        "src.txt"), path_wrapper.join("dest.txt"), follow_symlinks=True)


def test_mkdir(path_wrapper, mock_mkdir_success):
    path_wrapper.mkdir("new_dir")
    mock_mkdir_success.assert_called_once_with(
        path_wrapper.join("new_dir"), mode=511)


def test_makedirs(path_wrapper, mock_makedirs_success):
    path_wrapper.makedirs("new_dir", exist_ok=True)
    mock_makedirs_success.assert_called_once_with(
        path_wrapper.join("new_dir"), mode=511, exist_ok=True)


def test_copytree(path_wrapper, mock_copytree_success):
    path_wrapper.copytree("src_dir", "dest_dir")
    mock_copytree_success.assert_called_once_with(path_wrapper.join("src_dir"), path_wrapper.join(
        "dest_dir"), symlinks=False, ignore_dangling_symlinks=False, dirs_exist_ok=False)


def test_listdir(path_wrapper, mock_listdir_all):
    contents = path_wrapper.listdir(".")
    assert contents == LISTDIR_ALL


def test_rmtree(path_wrapper, mock_rmtree_success):
    path_wrapper.rmtree("old_dir")
    mock_rmtree_success.assert_called_once_with(
        path_wrapper.join("old_dir"), ignore_errors=False)


def test_wrap(path_wrapper):
    new_wrapper = path_wrapper.wrap("subdir")
    assert isinstance(new_wrapper, snr.core.core.path_wrapper.PathWrapperBase)
    assert new_wrapper._path == path_wrapper.join("subdir")
