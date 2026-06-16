import unittest
import sys
import os
import tempfile
import shutil
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from libs.whacipher import encrypt12, decrypt12

class TestWhacipher(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()

        # Paths for dummy files
        self.db_file = os.path.join(self.test_dir, 'msgstore.db')
        self.key_file = os.path.join(self.test_dir, 'key')
        self.db_cript = os.path.join(self.test_dir, 'msgstore.db.crypt12.dummy')
        self.output_file = os.path.join(self.test_dir, 'msgstore.db.crypt12.out')
        self.decrypted_file = os.path.join(self.test_dir, 'msgstore.db.decrypted')

        # 1. Create dummy db_file
        self.original_data = b"Hello WhatsApp! This is some dummy content to be encrypted."
        with open(self.db_file, "wb") as f:
            f.write(self.original_data)

        # 2. Create dummy key_file (158 bytes total, key is after 126, so 32 bytes for AES-256)
        # 126 bytes padding + 32 bytes key
        self.key_data = (b"A" * 126) + (b"B" * 32)
        with open(self.key_file, "wb") as f:
            f.write(self.key_data)

        # 3. Create dummy db_cript file (to extract header, IV, footer)
        # Header (51 bytes) + IV (16 bytes) + Dummy data (20 bytes) + Footer (20 bytes)
        # Total = 107 bytes. The footer will be the last 20 bytes.
        self.header = b"H" * 51
        self.iv = b"I" * 16
        self.dummy_enc = b"D" * 20
        self.footer = b"F" * 20
        self.db_cript_data = self.header + self.iv + self.dummy_enc + self.footer
        with open(self.db_cript, "wb") as f:
            f.write(self.db_cript_data)

        # Ensure cleanup runs even if setUp fails halfway
        self.addCleanup(shutil.rmtree, self.test_dir)

    @patch('builtins.print')
    def test_encrypt12_happy_path(self, mock_print):
        encrypt12(self.db_file, self.key_file, self.db_cript, self.output_file)

        # Check output file is created
        self.assertTrue(os.path.exists(self.output_file))

        # Check header, IV, and footer match
        with open(self.output_file, "rb") as f:
            out_data = f.read()

        self.assertEqual(out_data[:51], self.header)
        self.assertEqual(out_data[51:67], self.iv)
        self.assertEqual(out_data[-20:], self.footer)

    @patch('builtins.print')
    def test_encrypt12_and_decrypt12_roundtrip(self, mock_print):
        # First encrypt
        encrypt12(self.db_file, self.key_file, self.db_cript, self.output_file)
        self.assertTrue(os.path.exists(self.output_file))

        # Then decrypt
        decrypt12(self.output_file, self.key_file, self.decrypted_file)
        self.assertTrue(os.path.exists(self.decrypted_file))

        # Check contents match original
        with open(self.decrypted_file, "rb") as f:
            decrypted_data = f.read()

        self.assertEqual(decrypted_data, self.original_data)

    @patch('builtins.print')
    def test_encrypt12_error_handling(self, mock_print):
        # Use a non-existent file path to trigger an exception
        bad_file = os.path.join(self.test_dir, 'does_not_exist.db')

        encrypt12(bad_file, self.key_file, self.db_cript, self.output_file)

        # Output should not be created
        self.assertFalse(os.path.exists(self.output_file))

        # Verify that an error message was printed
        mock_print.assert_called()
        self.assertIn("[e] An error has ocurred encrypting", mock_print.call_args[0][0])

if __name__ == '__main__':
    unittest.main()