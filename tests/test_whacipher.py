import unittest
import sys
import os
from io import StringIO
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from libs.whacipher import banner, help

class TestWhacipher(unittest.TestCase):
    @patch('sys.stdout', new_callable=StringIO)
    def test_banner(self, mock_stdout):
        banner()
        self.assertIn("Whatsapp Encryption and Decryption", mock_stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_help(self, mock_stdout):
        help()
        self.assertIn("Author: Ivan Moreno a.k.a B16f00t", mock_stdout.getvalue())
        self.assertIn("Usage: python3 whacipher.py -h (for help)", mock_stdout.getvalue())

if __name__ == "__main__":
    unittest.main()
