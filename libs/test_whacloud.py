import unittest
import tempfile
import os
from libs.whacloud import is_media_tar

class TestIsMediaTar(unittest.TestCase):
    def test_is_media_tar_valid(self):
        """Test a valid tar file containing 'ustar' at the correct offset."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            data = b"a" * 257 + b"ustar" + b"b" * 3
            f.write(data)
            temp_name = f.name

        try:
            self.assertTrue(is_media_tar(temp_name))
        finally:
            os.remove(temp_name)

    def test_is_media_tar_x83(self):
        """Test an encrypted file starting with x83."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            data = b"\x83" + b"a" * 256 + b"ustar"
            f.write(data)
            temp_name = f.name

        try:
            self.assertFalse(is_media_tar(temp_name))
        finally:
            os.remove(temp_name)

    def test_is_media_tar_invalid(self):
        """Test a file that doesn't have 'ustar' at the expected offset."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            data = b"a" * 265
            f.write(data)
            temp_name = f.name

        try:
            self.assertFalse(is_media_tar(temp_name))
        finally:
            os.remove(temp_name)

    def test_is_media_tar_exception(self):
        """Test with a file path that causes an exception (e.g. doesn't exist)."""
        self.assertFalse(is_media_tar("non_existent_file.tar"))

if __name__ == '__main__':
    unittest.main()
