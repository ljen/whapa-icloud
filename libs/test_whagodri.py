import pytest
from whagodri import human_size

def test_human_size_bytes():
    assert human_size(0) == "(0 B)"
    assert human_size(10) == "(10 B)"
    assert human_size(1023) == "(1023 B)"
    assert human_size(-1023) == "(-1023 B)"

def test_human_size_kilobytes():
    assert human_size(1024) == "(1 kB)"
    assert human_size(2047) == "(1 kB)"
    assert human_size(-1024) == "(-1 kB)"

def test_human_size_megabytes():
    assert human_size(1024**2) == "(1 MB)"
    assert human_size(1024**2 * 1.5) == "(1 MB)"

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
