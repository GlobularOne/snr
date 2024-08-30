"""
Mock program_wrapper module
"""

import pytest
import pytest_mock

import snr.core.util.program_wrapper


@pytest.fixture
def mock_ProgramWrapperBase(mocker: pytest_mock.MockerFixture):
    return mocker.patch("snr.core.util.program_wrapper.ProgramWrapperBase",
                        spec=snr.core.util.program_wrapper.ProgramWrapperBase)
