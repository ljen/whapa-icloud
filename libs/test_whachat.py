from libs.whachat import system_slash


def test_system_slash_windows(mocker):
    # Test win32
    mocker.patch("sys.platform", "win32")
    assert system_slash("path/to/file") == "path\\to\\file"
    assert system_slash("path\\to\\file") == "path\\to\\file"

    # Test win64
    mocker.patch("sys.platform", "win64")
    assert system_slash("path/to/file") == "path\\to\\file"
    assert system_slash("path\\to\\file") == "path\\to\\file"

    # Test cygwin
    mocker.patch("sys.platform", "cygwin")
    assert system_slash("path/to/file") == "path\\to\\file"
    assert system_slash("path\\to\\file") == "path\\to\\file"


def test_system_slash_unix(mocker):
    # Test linux
    mocker.patch("sys.platform", "linux")
    assert system_slash("path\\to\\file") == "path/to/file"
    assert system_slash("path/to/file") == "path/to/file"

    # Test darwin
    mocker.patch("sys.platform", "darwin")
    assert system_slash("path\\to\\file") == "path/to/file"
    assert system_slash("path/to/file") == "path/to/file"
