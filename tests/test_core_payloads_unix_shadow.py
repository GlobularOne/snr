import snr.core.payload.unix_shadow


def test_unix_shadow_entry_init():
    entry = snr.core.payload.unix_shadow.UnixShadowEntry(
        login_name="testuser",
        password="hashedpassword",
        password_change_date="20230101",
        max_password_age="90",
        min_password_age="7",
        password_warn_period="14",
        password_inactivity_period="30",
        expiration_date="20240101",
        reserved="",
        locked=False
    )

    assert entry.login_name == "testuser"
    assert entry.password == "hashedpassword"
    assert entry.password_change_date == "20230101"
    assert entry.max_password_age == "90"
    assert entry.min_password_age == "7"
    assert entry.password_warn_period == "14"
    assert entry.password_inactivity_period == "30"
    assert entry.expiration_date == "20240101"
    assert entry.reserved == ""
    assert entry.locked is False


def test_unix_shadow_entry_str_locked():
    entry = snr.core.payload.unix_shadow.UnixShadowEntry(
        login_name="testuser",
        password="hashedpassword",
        password_change_date="20230101",
        max_password_age="90",
        min_password_age="7",
        password_warn_period="14",
        password_inactivity_period="30",
        expiration_date="20240101",
        reserved="",
        locked=True
    )

    assert str(entry) == "testuser:!hashedpassword:20230101:90:7:14:30:20240101:"


def test_unix_shadow_entry_str_unlocked():
    entry = snr.core.payload.unix_shadow.UnixShadowEntry(
        login_name="testuser",
        password="hashedpassword",
        password_change_date="20230101",
        max_password_age="90",
        min_password_age="7",
        password_warn_period="14",
        password_inactivity_period="30",
        expiration_date="20240101",
        reserved="",
        locked=False
    )

    assert str(entry) == "testuser:hashedpassword:20230101:90:7:14:30:20240101:"


def test_parse_unix_shadow_line():
    line = "testuser:hashedpassword:20230101:90:7:14:30:20240101:\n"
    entry = snr.core.payload.unix_shadow.parse_unix_shadow_line(line)

    assert entry.login_name == "testuser"
    assert entry.password == "hashedpassword"
    assert entry.password_change_date == "20230101"
    assert entry.max_password_age == "90"
    assert entry.min_password_age == "7"
    assert entry.password_warn_period == "14"
    assert entry.password_inactivity_period == "30"
    assert entry.expiration_date == "20240101"
    assert entry.reserved == ""
    assert entry.locked is False


def test_parse_unix_shadow_line_locked():
    line = "testuser:!hashedpassword:20230101:90:7:14:30:20240101:\n"
    entry = snr.core.payload.unix_shadow.parse_unix_shadow_line(line)

    assert entry.login_name == "testuser"
    assert entry.password == "hashedpassword"
    assert entry.locked is True


def test_parse_unix_shadow_file(mocker):
    mock_data = "testuser:hashedpassword:20230101:90:7:14:30:20240101:\n\n"
    new_open = mocker.patch("builtins.open",
                            new=mocker.mock_open(read_data=mock_data))
    shadows = snr.core.payload.unix_shadow.parse_unix_shadow_file()

    assert len(shadows) == 1
    assert shadows[0].login_name == "testuser"


def test_format_unix_shadow_line():
    entry = snr.core.payload.unix_shadow.UnixShadowEntry(
        login_name="testuser",
        password="hashedpassword",
        password_change_date="20230101",
        max_password_age="90",
        min_password_age="7",
        password_warn_period="14",
        password_inactivity_period="30",
        expiration_date="20240101",
        reserved="",
        locked=False
    )

    formatted_line = snr.core.payload.unix_shadow.format_unix_shadow_line(
        entry)
    assert formatted_line == "testuser:hashedpassword:20230101:90:7:14:30:20240101:"


def test_format_unix_shadow_file():
    entry = snr.core.payload.unix_shadow.UnixShadowEntry(
        login_name="testuser",
        password="hashedpassword",
        password_change_date="20230101",
        max_password_age="90",
        min_password_age="7",
        password_warn_period="14",
        password_inactivity_period="30",
        expiration_date="20240101",
        reserved="",
        locked=False
    )

    formatted_file = snr.core.payload.unix_shadow.format_unix_shadow_file([
                                                                          entry])
    assert formatted_file == "testuser:hashedpassword:20230101:90:7:14:30:20240101:\n"
