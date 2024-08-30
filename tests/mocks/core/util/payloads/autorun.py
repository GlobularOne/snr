"""
Mock autorun module
"""

import pytest
import pytest_mock

import snr.core.util.payloads.autorun


@pytest.fixture
def mock_Autorun(mocker: pytest_mock.MockerFixture):
    return mocker.patch("snr.core.util.payloads.autorun.Autorun",
                        spec=snr.core.util.payloads.autorun.Autorun)
