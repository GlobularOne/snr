"""
Mock path_wrapper module
"""

import pytest

import snr.core.core.path_wrapper

from ...stdlib.mock_builtins import *
from ...stdlib.mock_os import *
from ...stdlib.mock_os_path import *
from ...stdlib.mock_shutil import *


@pytest.fixture
def mock_PathWrapperBase_everything_works(mock_exists_true, mock_isdir_true, mock_isfile_true,
                                          mock_islink_true, mock_open, mock_remove_success,
                                          mock_link_success, mock_mkdir_success, mock_makedirs_success,
                                          mock_copytree_success, mock_listdir_all):
    return snr.core.core.path_wrapper.PathWrapperBase("/")


@pytest.fixture
def mock_module_core_core_path_wrapper(mock_PathWrapperBase_everything_works):
    pass
