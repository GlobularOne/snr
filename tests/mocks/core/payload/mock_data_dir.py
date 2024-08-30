"""
Mock data_dir module
"""

import pytest
import pytest_mock

from ..core.mock_path_wrapper import mock_PathWrapperBase_everything_works


@pytest.fixture
def mock_fix_data_dir_success(mocker: pytest_mock.MockerFixture):
    return mocker.patch("snr.core.payload.data_dir.fix_data_dir", return_value=None)


def mock_module_core_payload_data_dir(mock_fix_data_dir_success, mock_PathWrapperBase_everything_works):
    pass
