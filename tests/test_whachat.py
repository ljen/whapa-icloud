import pytest
from libs.whachat import startsWithDateTimeAndroid

def test_startsWithDateTimeAndroid_valid():
    assert startsWithDateTimeAndroid("24/5/18 14:25 - Sergio F: No se tío")
    assert startsWithDateTimeAndroid("24.07.21, 10:15 - Hello")
    assert startsWithDateTimeAndroid("12/12/2021 14:25 - Hey")
    assert startsWithDateTimeAndroid("1/1/20 1:2:3 - Msg")
    assert startsWithDateTimeAndroid("24/5/18 14:25 -")

def test_startsWithDateTimeAndroid_invalid():
    assert not startsWithDateTimeAndroid("Not a date - Hello")
    assert not startsWithDateTimeAndroid("24/5/18 14:25")
    assert not startsWithDateTimeAndroid("")
    assert not startsWithDateTimeAndroid("Sergio F: No se tío")
