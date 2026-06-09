import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from libs.whapa import duration_file

class TestDurationFile(unittest.TestCase):
    def test_seconds(self):
        self.assertEqual(duration_file(0), "0s")
        self.assertEqual(duration_file(1), "1s")
        self.assertEqual(duration_file(59), "59s")

    def test_minutes(self):
        self.assertEqual(duration_file(60), "1m 0s")
        self.assertEqual(duration_file(61), "1m 1s")
        self.assertEqual(duration_file(120), "2m 0s")
        self.assertEqual(duration_file(3599), "59m 59s")

    def test_hours(self):
        self.assertEqual(duration_file(3600), "1h 0m 0s")
        self.assertEqual(duration_file(3601), "1h 0m 1s")
        self.assertEqual(duration_file(3660), "1h 1m 0s")
        self.assertEqual(duration_file(3661), "1h 1m 1s")
        self.assertEqual(duration_file(7200), "2h 0m 0s")
        self.assertEqual(duration_file(7322), "2h 2m 2s")

if __name__ == '__main__':
    unittest.main()
