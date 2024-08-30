import snr.core.payload.unix_gshadow


def test_unix_gshadow_entry_init():
    entry = snr.core.payload.unix_gshadow.UnixGShadowEntry(
        group_name="testgroup",
        password="hashedpassword",
        administrators=("admin1", "admin2", "admin3"),
        members=("testuser1", "testuser2", "testuser3"),
        locked=False
    )

    assert entry.group_name == "testgroup"
    assert entry.password == "hashedpassword"
    assert entry.administrators == ["admin1", "admin2", "admin3"]
    assert entry.members == ["testuser1", "testuser2", "testuser3"]
    assert entry.locked is False


def test_unix_gshadow_entry_str_locked():
    entry = snr.core.payload.unix_gshadow.UnixGShadowEntry(
        group_name="testgroup",
        password="hashedpassword",
        administrators=("admin1", "admin2", "admin3"),
        members=("testuser1", "testuser2", "testuser3"),
        locked=True
    )

    assert str(
        entry) == "testgroup:!hashedpassword:admin1,admin2,admin3:testuser1,testuser2,testuser3"


def test_unix_gshadow_entry_str_unlocked():
    entry = snr.core.payload.unix_gshadow.UnixGShadowEntry(
        group_name="testgroup",
        password="hashedpassword",
        administrators=("admin1", "admin2", "admin3"),
        members=("testuser1", "testuser2", "testuser3"),
        locked=False
    )

    assert str(
        entry) == "testgroup:hashedpassword:admin1,admin2,admin3:testuser1,testuser2,testuser3"


def test_parse_unix_gshadow_line():
    line = "testgroup:hashedpassword:admin1,admin2,admin3:testuser1,testuser2,testuser3\n"
    entry = snr.core.payload.unix_gshadow.parse_unix_gshadow_line(line)

    assert entry.group_name == "testgroup"
    assert entry.password == "hashedpassword"
    assert entry.administrators == ["admin1", "admin2", "admin3"]
    assert entry.members == ["testuser1", "testuser2", "testuser3"]
    assert entry.locked is False


def test_parse_unix_gshadow_line_locked():
    line = "testgroup:!hashedpassword:admin1,admin2,admin3:testuser1,testuser2,testuser3\n"
    entry = snr.core.payload.unix_gshadow.parse_unix_gshadow_line(line)

    assert entry.group_name == "testgroup"
    assert entry.password == "hashedpassword"
    assert entry.locked is True


def test_parse_unix_gshadow_file(mocker):
    mock_data = "testgroup:!hashedpassword:admin1,admin2,admin3:testuser1,testuser2,testuser3\n\n"
    new_open = mocker.patch("builtins.open",
                            new=mocker.mock_open(read_data=mock_data))
    shadows = snr.core.payload.unix_gshadow.parse_unix_gshadow_file()

    assert len(shadows) == 1
    assert shadows[0].group_name == "testgroup"


def test_format_unix_gshadow_line():
    entry = snr.core.payload.unix_gshadow.UnixGShadowEntry(
        group_name="testgroup",
        password="hashedpassword",
        administrators=("admin1", "admin2", "admin3"),
        members=("testuser1", "testuser2", "testuser3"),
        locked=False
    )

    formatted_line = snr.core.payload.unix_gshadow.format_unix_gshadow_line(
        entry)
    assert formatted_line == "testgroup:hashedpassword:admin1,admin2,admin3:testuser1,testuser2,testuser3"


def test_format_unix_gshadow_file():
    entry = snr.core.payload.unix_gshadow.UnixGShadowEntry(
        group_name="testgroup",
        password="hashedpassword",
        administrators=("admin1", "admin2", "admin3"),
        members=("testuser1", "testuser2", "testuser3"),
        locked=False
    )

    formatted_file = snr.core.payload.unix_gshadow.format_unix_gshadow_file([
        entry])
    assert formatted_file == "testgroup:hashedpassword:admin1,admin2,admin3:testuser1,testuser2,testuser3\n"
