import pytest

import snr.core.core.variable_manager


@pytest.fixture
def variable_manager():
    """Fixture to create a VariableManager instance for testing."""
    return snr.core.core.variable_manager.VariableManager()


def test_initialization(variable_manager):
    assert variable_manager.get_variables_name() == []
    assert variable_manager.get_variables_value() == []
    assert variable_manager.get_variables_info() == []


def test_set_variable(variable_manager):
    variable_manager.set_variable(
        "test_var", "test_value", info_description="A test variable")
    assert variable_manager.has_variable("test_var")
    assert variable_manager.get_variable("test_var") == "test_value"
    info = variable_manager.get_variable_info("test_var")
    assert info.description == "A test variable"
    assert info.var_type == str


def test_set_variable_with_length(variable_manager):
    variable_manager.set_variable("test_var", "test_value", info_length=10)
    info = variable_manager.get_variable_info("test_var")
    assert info.length == 10


def test_set_variable_invalid_type(variable_manager):
    with pytest.raises(ValueError, match="Unsupported type '"):
        variable_manager.set_variable("test_var", 123.45)


def test_set_variable_type_mismatch(variable_manager):
    variable_manager.set_variable("test_var", "test_value")
    with pytest.raises(TypeError, match="'123' is not of type defined for variable"):
        variable_manager.set_variable("test_var", 123)


def test_get_variable(variable_manager):
    variable_manager.set_variable("test_var", "test_value")
    assert variable_manager.get_variable("test_var") == "test_value"


def test_get_variable_nonexistent(variable_manager):
    with pytest.raises(ValueError, match="No variable named 'nonexistent'"):
        variable_manager.get_variable("nonexistent")


def test_get_variable_info(variable_manager):
    variable_manager.set_variable("test_var", "test_value")
    info = variable_manager.get_variable_info("test_var")
    assert info.description == ""
    assert info.var_type == str


def test_get_variable_info_nonexistent(variable_manager):
    with pytest.raises(KeyError, match="No variable named 'nonexistent'"):
        variable_manager.get_variable_info("nonexistent")


def test_del_variable(variable_manager):
    variable_manager.set_variable("test_var", "test_value")
    variable_manager.del_variable("test_var")
    assert not variable_manager.has_variable("test_var")


def test_get_variables_name(variable_manager):
    variable_manager.set_variable("var1", "value1")
    variable_manager.set_variable("var2", "value2")
    assert set(variable_manager.get_variables_name()) == {"var1", "var2"}


def test_get_variables_value(variable_manager):
    variable_manager.set_variable("var1", "value1")
    variable_manager.set_variable("var2", "value2")
    assert variable_manager.get_variables_value() == ["value1", "value2"]


def test_get_variables_info(variable_manager):
    variable_manager.set_variable(
        "var1", "value1", info_description="First variable")
    variable_manager.set_variable(
        "var2", "value2", info_description="Second variable")
    infos = variable_manager.get_variables_info()
    assert len(infos) == 2
    assert infos[0].description == "First variable"
    assert infos[1].description == "Second variable"
