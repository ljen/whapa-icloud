import pytest
import unittest
from libs.whachat import startsWithDateTimeAndroid, getDataPointiOS

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

class TestGetDataPointiOS(unittest.TestCase):
    def test_english_format(self):
        line = "[25/8/20, 10:02:14] Jordi Subinspector Tecnologicos: Por qué no vieron los maniquiey"
        date, time, author, message = getDataPointiOS(line)
        self.assertEqual(date, "25/8/20")
        self.assertEqual(time, "10:02:14")
        self.assertEqual(author, "Jordi Subinspector Tecnologicos")
        self.assertEqual(message, "Por qué no vieron los maniquiey")

    def test_spanish_format(self):
        line = "[25/8/20 10:02:14] Jordi Subinspector: Hola"
        date, time, author, message = getDataPointiOS(line)
        self.assertEqual(date, "25/8/20")
        self.assertEqual(time, "10:02:14")
        self.assertEqual(author, "Jordi Subinspector")
        self.assertEqual(message, "Hola")

    def test_no_author(self):
        line = "[25/8/20, 10:02:14] Messages to this group are now secured with end-to-end encryption."
        date, time, author, message = getDataPointiOS(line)
        self.assertEqual(date, "25/8/20")
        self.assertEqual(time, "10:02:14")
        self.assertIsNone(author)
        self.assertEqual(message, "Messages to this group are now secured with end-to-end encryption.")

    def test_phone_number_author(self):
        line = "[25/8/20, 10:02:14] +34 666 555 444: Hello"
        date, time, author, message = getDataPointiOS(line)
        self.assertEqual(date, "25/8/20")
        self.assertEqual(time, "10:02:14")
        self.assertEqual(author, "+34 666 555 444")
        self.assertEqual(message, "Hello")

if __name__ == '__main__':
    unittest.main()
