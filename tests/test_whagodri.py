import unittest
from unittest.mock import patch
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'libs')))
import whagodri

class TestOperatingSystem(unittest.TestCase):

    @patch('whagodri.sys.platform', 'win32')
    def test_windows_win32(self):
        self.assertEqual(whagodri.operating_system(), 'Windows')

    @patch('whagodri.sys.platform', 'cygwin')
    def test_windows_cygwin(self):
        self.assertEqual(whagodri.operating_system(), 'Windows')

    @patch('whagodri.sys.platform', 'Darwin')
    @patch('whagodri.subprocess.check_output')
    def test_macos_m1(self, mock_check_output):
        mock_check_output.return_value = b'Apple M1\n'
        self.assertEqual(whagodri.operating_system(), 'MacOs M1')
        mock_check_output.assert_called_once_with(['sysctl', '-n', 'machdep.cpu.brand_string'])

    @patch('whagodri.sys.platform', 'Darwin')
    @patch('whagodri.subprocess.check_output')
    def test_macos_intel(self, mock_check_output):
        mock_check_output.return_value = b'Intel\n'
        self.assertEqual(whagodri.operating_system(), 'MacOs')
        mock_check_output.assert_called_once_with(['sysctl', '-n', 'machdep.cpu.brand_string'])

    @patch('whagodri.sys.platform', 'linux')
    def test_linux(self):
        self.assertEqual(whagodri.operating_system(), 'Linux')

if __name__ == '__main__':
    unittest.main()
