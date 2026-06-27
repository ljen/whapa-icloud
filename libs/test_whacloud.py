import unittest
import tempfile
import os
import binascii
from libs.whacloud import is_media_tar, hkdf_legacy


class TestHkdfLegacy(unittest.TestCase):
    def test_hkdf_legacy_basic(self):
        """Test basic hkdf_legacy functionality with known vectors."""
        ikm = b"password"
        salt = b"salt"
        info = b"info"
        length = 32
        expected = binascii.unhexlify(
            b"afae921b3bebb39989e1edba7b98344b227ff0a6d42739b6628098bc8377037b"
        )
        result = hkdf_legacy(ikm, salt, info, length)
        self.assertEqual(result, expected)
        self.assertEqual(len(result), length)

    def test_hkdf_legacy_none_salt(self):
        """Test hkdf_legacy when salt is None (defaults to b'\\x00'*32)."""
        ikm = b"password"
        info = b"info"
        length = 32
        expected = binascii.unhexlify(
            b"6383ecb00b8f97c8046a02f7caa46ebd180aae52de5b0b85f742195854767bf1"
        )
        result = hkdf_legacy(ikm, None, info, length)
        self.assertEqual(result, expected)
        self.assertEqual(len(result), length)

        # Verify it matches explicit 32 bytes of zeros
        explicit_salt_result = hkdf_legacy(ikm, b"\x00" * 32, info, length)
        self.assertEqual(result, explicit_salt_result)

    def test_hkdf_legacy_length(self):
        """Test hkdf_legacy returns correct lengths."""
        ikm = b"test_key_material"
        salt = b"test_salt"
        info = b"test_info"

        for length in [16, 32, 48, 64]:
            result = hkdf_legacy(ikm, salt, info, length)
            self.assertEqual(len(result), length)


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


if __name__ == "__main__":
    unittest.main()
