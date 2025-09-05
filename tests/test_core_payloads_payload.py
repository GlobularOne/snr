import os

import pytest

import snr.cli.variables
import snr.core.core.context
import snr.core.core.variable_manager
import snr.core.payload.payload
import snr.core.util.common_utils

from .mocks.core.util.mock_common_utils import *
from .mocks.core.util.payloads.autorun import *
from .mocks.psutil import *
from .mocks.stdlib.mock_builtins import *
from .mocks.stdlib.mock_shutil import *


@pytest.fixture
def mock_global_vars(mocker):
    mocker.patch('snr.cli.variables.global_vars',
                 new_callable=mocker.MagicMock)
    return snr.cli.variables.global_vars


@pytest.fixture
def temp_global_vars(mocker):
    mocker.patch('snr.cli.variables.global_vars',
                 new=snr.core.core.variable_manager.VariableManager())
    return snr.cli.variables.global_vars


@pytest.fixture
def mock_context(mocker):
    return mocker.MagicMock(spec=snr.core.core.context.Context)


@pytest.fixture
def payload_instance():
    return snr.core.payload.payload.Payload()


def test_load(payload_instance, mock_global_vars):
    payload_instance.INPUT = (
        ("var1", "default1", 10, "Variable 1"),
        ("var2", "default2", 20, "Variable 2",
         snr.core.core.variable_manager.VariableFlags.VALID_STRING),
        ("var3", "default3", 30, "Variable 3", True)
    )

    result = payload_instance.load()

    assert result == 0
    mock_global_vars.set_variable.assert_any_call(
        "var1", "default1", 10, "Variable 1",
        snr.core.core.variable_manager.VariableFlags.USED_BY_PAYLOAD)
    mock_global_vars.set_variable.assert_any_call(
        "var2", "default2", 20, "Variable 2",
        snr.core.core.variable_manager.VariableFlags.USED_BY_PAYLOAD | snr.core.core.variable_manager.VariableFlags.VALID_STRING)


def test_load_invalid(payload_instance, temp_global_vars):

    payload_instance.INPUT = (
        ("var1", "", -1, "Variable 1", True, True),
    )
    with pytest.raises(snr.core.util.common_utils.UserError):
        payload_instance.load()


def test_unload(payload_instance, mock_global_vars):
    payload_instance.INPUT = (
        ("var1", "default1", 10, "Variable 1"),
        ("var2", "default2", 20, "Variable 2")
    )

    result = payload_instance.unload()

    assert result == 0
    mock_global_vars.del_variable.assert_any_call("var1")
    mock_global_vars.del_variable.assert_any_call("var2")


@pytest.mark.parametrize('value,flags,should_fail,expected_value',
                         (
                             (False, snr.core.core.variable_manager.VariableFlags.NORMAL, False, False),
                             ("default", snr.core.core.variable_manager.VariableFlags.VALID_STRING,
                              False, "default"),
                             ("default", snr.core.core.variable_manager.VariableFlags.VALID_STRING |
                              snr.core.core.variable_manager.VariableFlags.REQUIRED, True, "default"),
                             ("", snr.core.core.variable_manager.VariableFlags.VALID_STRING, True, ""),
                             ("default", snr.core.core.variable_manager.VariableFlags.VALID_ALPHA,
                              False, "default"),
                             ("default1", snr.core.core.variable_manager.VariableFlags.VALID_ALPHA,
                              True, "default1"),
                             ("defaul t", snr.core.core.variable_manager.VariableFlags.VALID_ALPHA,
                              True, "defaul t"),
                             ("default!", snr.core.core.variable_manager.VariableFlags.VALID_ALPHA,
                              True, "default!"),
                             ("", snr.core.core.variable_manager.VariableFlags.VALID_ALPHA, True, ""),
                             ("default", snr.core.core.variable_manager.VariableFlags.VALID_ALPHANUM,
                              False, "default"),
                             ("default1", snr.core.core.variable_manager.VariableFlags.VALID_ALPHANUM,
                              False, "default1"),
                             ("defaul t", snr.core.core.variable_manager.VariableFlags.VALID_ALPHANUM,
                              True, "defaul t"),
                             ("default!", snr.core.core.variable_manager.VariableFlags.VALID_ALPHANUM,
                              True, "default!"),
                             ("", snr.core.core.variable_manager.VariableFlags.VALID_ALPHANUM, True, ""),
                             ("default", snr.core.core.variable_manager.VariableFlags.VALID_ASCII,
                              False, "default"),
                             ("default1", snr.core.core.variable_manager.VariableFlags.VALID_ASCII,
                              False, "default1"),
                             ("defaul t", snr.core.core.variable_manager.VariableFlags.VALID_ASCII,
                              False, "defaul t"),
                             ("default!", snr.core.core.variable_manager.VariableFlags.VALID_ASCII,
                              False, "default!"),
                             ("\u00E9", snr.core.core.variable_manager.VariableFlags.VALID_ASCII, True, "\u00E9"),
                             ("default", snr.core.core.variable_manager.VariableFlags.VALID_PATH_COMPONENT,
                              False, "default"),
                             ("default1", snr.core.core.variable_manager.VariableFlags.VALID_PATH_COMPONENT,
                              False, "default1"),
                             ("defaul t", snr.core.core.variable_manager.VariableFlags.VALID_PATH_COMPONENT,
                              False, "defaul t"),
                             ("default!", snr.core.core.variable_manager.VariableFlags.VALID_PATH_COMPONENT,
                              False, "default!"),
                             ("", snr.core.core.variable_manager.VariableFlags.VALID_PATH_COMPONENT, True, ""),
                             ("../", snr.core.core.variable_manager.VariableFlags.VALID_PATH_COMPONENT, True, "../"),
                             ("*", snr.core.core.variable_manager.VariableFlags.VALID_PATH_COMPONENT, True, "*"),
                             ("\\", snr.core.core.variable_manager.VariableFlags.VALID_PATH_COMPONENT, True, "\\"),
                             ("/", snr.core.core.variable_manager.VariableFlags.VALID_LOCAL_PATH, False, "/"),
                             ("/nonexistent", snr.core.core.variable_manager.VariableFlags.VALID_LOCAL_PATH,
                              True, "/nonexistent"),
                             ("/", snr.core.core.variable_manager.VariableFlags.VALID_HOST_PATH, False, "/"),
                             ("/nonexistent", snr.core.core.variable_manager.VariableFlags.VALID_HOST_PATH,
                              True, "/nonexistent"),
                             ("/nonexistent", snr.core.core.variable_manager.VariableFlags.VALID_PORT,
                              False, "/nonexistent"),
                             ("127.0.0.1", snr.core.core.variable_manager.VariableFlags.VALID_IP,
                              False, "127.0.0.1"),
                             ("localhost", snr.core.core.variable_manager.VariableFlags.VALID_IP,
                              False, "127.0.0.1"),
                             ("lo", snr.core.core.variable_manager.VariableFlags.VALID_IP,
                              False, "127.0.0.1"),
                             ("lox", snr.core.core.variable_manager.VariableFlags.VALID_IP,
                              True, "127.0.0.1"),
                             ("127.0.0.1", snr.core.core.variable_manager.VariableFlags.VALID_IPV4,
                              False, "127.0.0.1"),
                             ("localhost", snr.core.core.variable_manager.VariableFlags.VALID_IPV4,
                              False, "127.0.0.1"),
                             ("lo", snr.core.core.variable_manager.VariableFlags.VALID_IPV4,
                              False, "127.0.0.1"),
                             ("lox", snr.core.core.variable_manager.VariableFlags.VALID_IPV4,
                              True, "127.0.0.1"),
                             ("::1", snr.core.core.variable_manager.VariableFlags.VALID_IPV6, False, "::1"),
                             ("ip6-localhost", snr.core.core.variable_manager.VariableFlags.VALID_IPV6, False, "::1"),
                             ("lo", snr.core.core.variable_manager.VariableFlags.VALID_IPV6, False, "::1"),
                             ("lox", snr.core.core.variable_manager.VariableFlags.VALID_IPV6, True, "::1"),
                             (["default", "default2", "default3"], snr.core.core.variable_manager.VariableFlags.VALID_STRING, False, [
                              "default", "default2", "default3"]),
                             ("eth0", snr.core.core.variable_manager.VariableFlags.VALID_IP,
                              True, "127.0.0.1"),
                             ("eth0", snr.core.core.variable_manager.VariableFlags.VALID_IPV4,
                              True, "127.0.0.1"),
                             ("eth0", snr.core.core.variable_manager.VariableFlags.VALID_IPV6,
                              True, "127.0.0.1"),
                         )
                         )
def test_validate_string_variable(mock_print_warning, value, flags, should_fail, expected_value,
                                  payload_instance, mock_context, temp_global_vars, mock_net_if_addrs_list1, mock_net_if_stats_list1,
                                  mocker):
    def gethostbyname(name: str):
        if name == "localhost":
            return "127.0.0.1"
        raise socket.gaierror

    def getaddrinfo(name: str, *_,):
        if name == "ip6-localhost":
            return (
                ("whatever", "whatever", "whatever", "whatever", ("::1", 0, 0, 0)),
            )
        raise socket.gaierror
    mock_gethostbyname = mocker.patch(
        "socket.gethostbyname", new=gethostbyname)
    mock_getaddrinfo = mocker.patch(
        "socket.getaddrinfo", new=getaddrinfo)
    payload_instance.INPUT = (
        ("var1", value, -1, "Variable 1", flags),
    )

    payload_instance.load()
    if should_fail:
        with pytest.raises(snr.core.util.common_utils.UserError):
            mock_context.exists = lambda x: False if x.startswith(
                "/nonexistent") else True
            payload_instance.validate(mock_context)
            if flags & snr.core.core.variable_manager.VariableFlags.VALID_PORT:
                mock_print_warning.assert_called_once()
            else:
                mock_print_warning.assert_not_called()
    else:
        result = payload_instance.validate(mock_context)
        assert result["var1"] == expected_value


def test_generate(payload_instance, mock_context):
    with pytest.raises(NotImplementedError):
        payload_instance.generate(mock_context)


@pytest.mark.parametrize('value,flags,should_fail,expected_value',
                         (
                             (80, snr.core.core.variable_manager.VariableFlags.VALID_PORT, False, 80),
                             (65535, snr.core.core.variable_manager.VariableFlags.VALID_PORT, True, 6535),
                         )
                         )
def test_validate_int_variable(mock_print_warning, value, flags, should_fail, expected_value,
                               payload_instance, mock_context, temp_global_vars):

    payload_instance.INPUT = (
        ("var1", value, -1, "Variable 1", flags),
    )

    payload_instance.load()
    if should_fail:
        with pytest.raises(snr.core.util.common_utils.UserError):
            payload_instance.validate(mock_context)
    else:
        result = payload_instance.validate(mock_context)
        assert result["var1"] == expected_value


def test_generate(payload_instance, mock_context):
    with pytest.raises(NotImplementedError):
        payload_instance.generate(mock_context)


def test_supports_encrypted_access(payload_instance):
    value = payload_instance.supports_encrypted_access()
    assert len(value) in (4, 5)
    assert isinstance(value[0], str)
    assert isinstance(value[1], list)
    assert isinstance(value[2], int)
    assert isinstance(value[3], str)


def test_copy_root_to_root(payload_instance, mock_context, mock_copyfile_success):
    module_path = "path/to/module/__init__.py"
    src = "source_file.txt"
    dest = "destination_file.txt"

    result = payload_instance.copy_root_to_root(
        mock_context, module_path, src, dest)

    mock_copyfile_success.assert_called_once_with(os.path.join(os.path.dirname(
        module_path), src), mock_context.join(dest), follow_symlinks=True)


def test_format_payload_and_write(payload_instance, mock_context, mock_open):
    data = {"key": "value"}
    local_payload_path = "local_payload.py"
    host_payload_path = "host_payload.py"

    payload_instance.format_payload_and_write(
        mock_context, data, local_payload_path, host_payload_path)
    mock_open.assert_called_once()


def test_get_self_variables(payload_instance, mock_context, temp_global_vars):
    payload_instance.INPUT = (
        ("var1", "default", 10, "Variable 1",
         snr.core.core.variable_manager.VariableFlags.VALID_STRING),
    )
    payload_instance.load()
    payload_instance.validate(mock_context)
    validated_vars = payload_instance.get_self_variables()
    assert validated_vars["var1"] == "default"


def test_add_autorun(mock_Autorun, payload_instance, mock_context):
    payload_instance.add_autorun(mock_context)
    payload_instance.add_autorun(mock_context)
