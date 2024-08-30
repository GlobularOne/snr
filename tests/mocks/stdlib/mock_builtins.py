"""
Mock builtins module
"""

import pytest
import pytest_mock

INPUT_STRING = "value"


@pytest.fixture
def mock_open(mocker: pytest_mock.MockerFixture):
    return mocker.patch("builtins.open", new=mocker.mock_open())


@pytest.fixture
def mock_input_empty(mocker: pytest_mock.MockerFixture):
    return mocker.patch("builtins.input", return_value="")


@pytest.fixture
def mock_input_string(mocker: pytest_mock.MockerFixture):
    return mocker.patch("builtins.input", return_value=INPUT_STRING)

@pytest.fixture
def mock_input_interrupt(mocker: pytest_mock.MockerFixture):
    return mocker.patch("builtins.input", side_effect=KeyboardInterrupt)

@pytest.fixture
def mock_input_string_then_interrupt(mocker: pytest_mock.MockerFixture):
    def new_input():
        if(hasattr(input, "do_interrupt")):
            raise KeyboardInterrupt
        setattr(input, "do_interrupt", True)
        return INPUT_STRING
        
    return mocker.patch("builtins.input", new=new_input)


@pytest.fixture
def mock_input_eof(mocker: pytest_mock.MockerFixture):
    return mocker.patch("builtins.input", side_effect=EOFError)
