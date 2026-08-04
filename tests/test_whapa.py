import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from colorama import Fore

from libs.whapa import duration_file, size_file, status


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


class TestWhapa(unittest.TestCase):
    def test_size_file(self):
        # Edge cases and values ​​in KB
        self.assertEqual(size_file(0), "(0.00 KB)")
        self.assertEqual(size_file(1024), "(1.00 KB)")
        self.assertEqual(size_file(1048576), "(1024.00 KB)")

        # Values ​​in MB
        self.assertEqual(size_file(1048577), "(1.00 MB)")
        self.assertEqual(size_file(2097152), "(2.00 MB)")


class TestStatus(unittest.TestCase):
    def test_status_received(self):
        # 0 and 5 return ("Received", "&#10004;&#10004;")
        self.assertEqual(status(0), ("Received", "&#10004;&#10004;"))
        self.assertEqual(status(5), ("Received", "&#10004;&#10004;"))

    def test_status_waiting_in_server(self):
        # 4 returns (Fore.RED + "Waiting in server" + Fore.RESET, "&#10004;")
        self.assertEqual(
            status(4), (Fore.RED + "Waiting in server" + Fore.RESET, "&#10004;")
        )

    def test_status_system_message(self):
        # 6 returns (Fore.YELLOW + "System message" + Fore.RESET, "&#128187;")
        self.assertEqual(
            status(6), (Fore.YELLOW + "System message" + Fore.RESET, "&#128187;")
        )

    def test_status_audio_played(self):
        # 8 and 10 return (Fore.BLUE + "Audio played" + Fore.RESET, "<font color=\"#0000ff \">&#10004;&#10004;</font>")
        expected = (
            Fore.BLUE + "Audio played" + Fore.RESET,
            '<font color="#0000ff ">&#10004;&#10004;</font>',
        )
        self.assertEqual(status(8), expected)
        self.assertEqual(status(10), expected)

    def test_status_seen(self):
        # 12 and 13 return (Fore.BLUE + "Seen" + Fore.RESET, "<font color=\"#0000ff \">&#10004;&#10004;</font>")
        expected = (
            Fore.BLUE + "Seen" + Fore.RESET,
            '<font color="#0000ff ">&#10004;&#10004;</font>',
        )
        self.assertEqual(status(12), expected)
        self.assertEqual(status(13), expected)

    def test_status_fallback(self):
        # any other number returns the string version of the number and an empty string
        self.assertEqual(status(1), ("1", ""))
        self.assertEqual(status(99), ("99", ""))
        self.assertEqual(status(-1), ("-1", ""))


if __name__ == "__main__":
    unittest.main()
