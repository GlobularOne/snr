import snr.core.payload.entry_point

from .mocks.core.payload.mock_data_dir import *
from .mocks.core.payload.mock_safety_pin import *
from .mocks.core.payload.mock_storage import *
from .mocks.core.util.mock_common_utils import *


def sample_function(block_info, root_ctx, our_device):
    return "Function executed"


def error_function(block_info, root_ctx, our_device):
    raise ValueError("An error occurred")


def no_param_function():
    return "No param function executed"


def test_entry_point_with_three_parameters(mock_handle_exception, mock_require_lack_of_safety_pin_success,
                                           mock_fix_data_dir_success, mock_setup_list1,
                                           mock_print_debug, mock_print_ok):
    snr.core.payload.entry_point.entry_point(sample_function)()
    mock_handle_exception.assert_not_called()
    mock_require_lack_of_safety_pin_success.assert_called_once()
    mock_fix_data_dir_success.assert_called_once()
    mock_setup_list1.assert_called_once_with(no_lvm=False)
    mock_print_debug.assert_called_once_with("Payload started")
    mock_print_ok.assert_called_once_with("Payload completed")


def test_entry_point_with_no_parameters(mock_handle_exception, mock_require_lack_of_safety_pin_success,
                                        mock_fix_data_dir_success, mock_setup_list1,
                                        mock_print_debug, mock_print_ok):
    snr.core.payload.entry_point.entry_point(no_param_function)()
    mock_handle_exception.assert_not_called()
    mock_require_lack_of_safety_pin_success.assert_called_once()
    mock_fix_data_dir_success.assert_called_once()
    mock_print_debug.assert_called_once_with("Payload started")
    mock_print_ok.assert_called_once_with("Payload completed")


def test_entry_point_exception_handling(mock_handle_exception, mock_require_lack_of_safety_pin_success,
                                        mock_fix_data_dir_success, mock_setup_list1,
                                        mock_print_debug, mock_print_ok):
    snr.core.payload.entry_point.entry_point(no_lvm=True)(error_function)()
    mock_require_lack_of_safety_pin_success.assert_called_once()
    mock_fix_data_dir_success.assert_called_once()
    mock_handle_exception.assert_called_once()
    mock_print_debug.assert_called_once_with("Payload started")
    mock_print_ok.assert_not_called()
