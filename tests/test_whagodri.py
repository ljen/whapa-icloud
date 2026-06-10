import pytest
from libs.whagodri import human_size

def test_human_size_bytes():
    assert human_size(0) == "(0 B)"
    assert human_size(1) == "(1 B)"
    assert human_size(1023) == "(1023 B)"

def test_human_size_kilobytes():
    assert human_size(1024) == "(1 kB)"
    assert human_size(2048) == "(2 kB)"
    assert human_size(1048575) == "(1023 kB)"

def test_human_size_megabytes():
    assert human_size(1048576) == "(1 MB)"
    assert human_size(1048576 * 2) == "(2 MB)"

def test_human_size_gigabytes():
    assert human_size(1024**3) == "(1 GB)"

def test_human_size_terabytes():
    assert human_size(1024**4) == "(1 TB)"

def test_human_size_petabytes():
    assert human_size(1024**5) == "(1 PB)"

def test_human_size_exabytes():
    assert human_size(1024**6) == "(1 EB)"

def test_human_size_zettabytes():
    assert human_size(1024**7) == "(1 ZB)"

def test_human_size_yottabytes():
    assert human_size(1024**8) == "(1 YB)"

def test_human_size_exceeding_yottabytes():
    assert human_size(1024**9) == "(1 YB)"
    assert human_size(1024**10) == "(1024 YB)"

def test_human_size_negative():
    assert human_size(-1) == "(-1 B)"
    assert human_size(-1023) == "(-1023 B)"
    assert human_size(-1024) == "(-1 kB)"
    assert human_size(-1048576) == "(-1 MB)"
