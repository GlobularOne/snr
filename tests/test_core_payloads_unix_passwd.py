import snr.core.payload.unix_passwd


def test_unix_passwd_entry_init():
    entry = snr.core.payload.unix_passwd.UnixPasswdEntry(
        login_name="testuser",
        password="x",
        uid=1000,
        gid=1000,
        comment="",
        home="/home/testuser",
        shell="/bin/bash",
        locked=False
    )
    assert entry.is_password_stored_in_shadow() == True
    assert entry.login_name == "testuser"
    assert entry.password == "x"
    assert entry.uid == 1000
    assert entry.gid == 1000
    assert entry.comment == ""
    assert entry.home == "/home/testuser"
    assert entry.shell == "/bin/bash"
    assert entry.locked == False


def test_unix_passwd_entry_str_locked():
    entry = snr.core.payload.unix_passwd.UnixPasswdEntry(
        login_name="testuser",
        password="x",
        uid=1000,
        gid=1000,
        comment="",
        home="/home/testuser",
        shell="/bin/bash",
        locked=True
    )

    assert str(entry) == "testuser:!x:1000:1000::/home/testuser:/bin/bash"


def test_unix_passwd_entry_str_unlocked():
    entry = snr.core.payload.unix_passwd.UnixPasswdEntry(
        login_name="testuser",
        password="x",
        uid=1000,
        gid=1000,
        comment="",
        home="/home/testuser",
        shell="/bin/bash",
        locked=False
    )

    assert str(entry) == "testuser:x:1000:1000::/home/testuser:/bin/bash"


def test_parse_unix_passwd_line():
    line = "testuser:x:1000:1000::/home/testuser:/bin/bash\n"
    entry = snr.core.payload.unix_passwd.parse_unix_passwd_line(line)

    assert entry.login_name == "testuser"
    assert entry.password == "x"
    assert entry.uid == 1000
    assert entry.gid == 1000
    assert entry.comment == ""
    assert entry.home == "/home/testuser"
    assert entry.shell == "/bin/bash"
    assert entry.locked == False


def test_parse_unix_passwd_line_locked():
    line = "testuser:!x:1000:1000::/home/testuser:/bin/bash\n"
    entry = snr.core.payload.unix_passwd.parse_unix_passwd_line(line)

    assert entry.login_name == "testuser"
    assert entry.password == "x"
    assert entry.locked is True


def test_parse_unix_passwd_file(mocker):
    mock_data = "testuser:x:1000:1000::/home/testuser:\n\n"
    new_open = mocker.patch("builtins.open",
                            new=mocker.mock_open(read_data=mock_data))
    shadows = snr.core.payload.unix_passwd.parse_unix_passwd_file()

    assert len(shadows) == 1
    assert shadows[0].login_name == "testuser"


def test_format_unix_passwd_line():
    entry = snr.core.payload.unix_passwd.UnixPasswdEntry(
        login_name="testuser",
        password="x",
        uid=1000,
        gid=1000,
        comment="",
        home="/home/testuser",
        shell="/bin/bash",
        locked=False
    )

    formatted_line = snr.core.payload.unix_passwd.format_unix_passwd_line(
        entry)
    assert formatted_line == "testuser:x:1000:1000::/home/testuser:/bin/bash"


def test_format_unix_passwd_file():
    entry = snr.core.payload.unix_passwd.UnixPasswdEntry(
        login_name="testuser",
        password="x",
        uid=1000,
        gid=1000,
        comment="",
        home="/home/testuser",
        shell="/bin/bash",
        locked=False
    )

    formatted_file = snr.core.payload.unix_passwd.format_unix_passwd_file([
                                                                          entry])
    assert formatted_file == "testuser:x:1000:1000::/home/testuser:/bin/bash\n"
