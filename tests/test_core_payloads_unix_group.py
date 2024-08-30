import snr.core.payload.unix_group


def test_unix_group_entry_init():
    entry = snr.core.payload.unix_group.UnixGroupEntry(
        group_name="testgroup",
        password="hashedpassword",
        gid=1000,
        user_list=("testuser1", "testuser2", "testuser3")
    )

    assert entry.group_name == "testgroup"
    assert entry.password == "hashedpassword"
    assert entry.gid == 1000
    assert entry.user_list == ["testuser1", "testuser2", "testuser3"]


def test_unix_group_entry_str():
    entry = snr.core.payload.unix_group.UnixGroupEntry(
        group_name="testgroup",
        password="hashedpassword",
        gid=1000,
        user_list=("testuser1", "testuser2", "testuser3")
    )

    assert str(
        entry) == "testgroup:hashedpassword:1000:testuser1,testuser2,testuser3"


def test_parse_unix_group_line():
    line = "testgroup:hashedpassword:1000:testuser1,testuser2,testuser3\n"
    entry = snr.core.payload.unix_group.parse_unix_group_line(line)

    assert entry.group_name == "testgroup"
    assert entry.password == "hashedpassword"
    assert entry.gid == 1000
    assert entry.user_list == ["testuser1", "testuser2", "testuser3"]


def test_parse_unix_group_file(mocker):
    mock_data = "testgroup:hashedpassword:1000:testuser1,testuser2,testuser3\n\n"
    new_open = mocker.patch("builtins.open",
                            new=mocker.mock_open(read_data=mock_data))
    shadows = snr.core.payload.unix_group.parse_unix_group_file()

    assert len(shadows) == 1
    assert shadows[0].group_name == "testgroup"


def test_format_unix_group_line():
    entry = snr.core.payload.unix_group.UnixGroupEntry(
        group_name="testgroup",
        password="hashedpassword",
        gid=1000,
        user_list=("testuser1", "testuser2", "testuser3")
    )

    formatted_line = snr.core.payload.unix_group.format_unix_group_line(
        entry)
    assert formatted_line == "testgroup:hashedpassword:1000:testuser1,testuser2,testuser3"


def test_format_unix_group_file():
    entry = snr.core.payload.unix_group.UnixGroupEntry(
        group_name="testgroup",
        password="hashedpassword",
        gid=1000,
        user_list=("testuser1", "testuser2", "testuser3")
    )

    formatted_file = snr.core.payload.unix_group.format_unix_group_file([
        entry])
    assert formatted_file == "testgroup:hashedpassword:1000:testuser1,testuser2,testuser3\n"
