from libs.whachat import system_slash


def test_system_slash_windows(mocker):
    # test win32
    mocker.patch("sys.platform", "win32")
    assert system_slash("path/to/file") == "path\\to\\file"
    assert system_slash("path\\to\\file") == "path\\to\\file"

    # test win64
    mocker.patch("sys.platform", "win64")
    assert system_slash("path/to/file") == "path\\to\\file"
    assert system_slash("path\\to\\file") == "path\\to\\file"

    # Cygwin test
    mocker.patch("sys.platform", "cygwin")
    assert system_slash("path/to/file") == "path\\to\\file"
    assert system_slash("path\\to\\file") == "path\\to\\file"


def test_system_slash_unix(mocker):
    # linux test
    mocker.patch("sys.platform", "linux")
    assert system_slash("path\\to\\file") == "path/to/file"
    assert system_slash("path/to/file") == "path/to/file"

    # darwin test
    mocker.patch("sys.platform", "darwin")
    assert system_slash("path\\to\\file") == "path/to/file"
    assert system_slash("path/to/file") == "path/to/file"
