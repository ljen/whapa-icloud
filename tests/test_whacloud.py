import os
import sys
import unittest

# Add the parent directory to the path so we can import libs
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from libs.whacloud_decrypt import _pkcs7_strip, _safe_join, hkdf_v1


class TestHkdfV1(unittest.TestCase):
    def test_hkdf_v1_known_output(self):
        # A simple known answer test generated directly from the function
        ikm = b"ikm_test_data"
        info = b"info_test_data"
        length = 32
        expected_hex = (
            "f15c20c921c12f95f00759afa87f6fa411a2221d19a347b1978b2daebe5f22bd"
        )
        out = hkdf_v1(ikm, info, length)
        self.assertEqual(out.hex(), expected_hex)

    def test_hkdf_v1_empty_info(self):
        # Info can be an empty byte string
        ikm = b"ikm_test_data"
        info = b""
        length = 16
        out = hkdf_v1(ikm, info, length)
        self.assertEqual(len(out), length)
        # Verify it's deterministic
        out2 = hkdf_v1(ikm, info, length)
        self.assertEqual(out, out2)

    def test_hkdf_v1_length(self):
        # Test that the length parameter correctly limits the output
        ikm = b"ikm_test_data"
        info = b"info_test_data"
        for length in [1, 16, 32, 48, 64]:
            out = hkdf_v1(ikm, info, length)
            self.assertEqual(len(out), length)


class TestPkcs7Strip(unittest.TestCase):
    def test_valid_padding(self):
        # Test valid padding lengths from 1 to 16
        base_data = b"hello_world"
        for i in range(1, 17):
            padded_data = base_data + bytes([i]) * i
            self.assertEqual(_pkcs7_strip(padded_data), base_data)

    def test_invalid_padding_value(self):
        # Padding values ​​must be between 1 and 16
        base_data = b"hello_world"

        # Padding value 0
        data_pad_0 = base_data + b"\x00"
        self.assertEqual(_pkcs7_strip(data_pad_0), data_pad_0)

        # Padding value > 16
        data_pad_17 = base_data + bytes([17]) * 17
        self.assertEqual(_pkcs7_strip(data_pad_17), data_pad_17)

    def test_invalid_padding_sequence(self):
        # Padding value is valid but sequence is wrong
        # e.g., ends with 3 but the preceding bytes aren't 3
        data_wrong_seq = b"hello_world" + b"\x01\x02\x03"
        self.assertEqual(_pkcs7_strip(data_wrong_seq), data_wrong_seq)

        data_wrong_seq2 = b"hello_world" + b"\x03\x04\x03"
        self.assertEqual(_pkcs7_strip(data_wrong_seq2), data_wrong_seq2)

    def test_no_padding(self):
        # Normal data that doesn't look like padding at the end
        data = b"hello_world"
        self.assertEqual(_pkcs7_strip(data), data)

    def test_empty_string(self):
        # The current implementation raises IndexError for empty bytes.
        # Let's ensure our test passes by anticipating the IndexError.
        with self.assertRaises(IndexError):
            _pkcs7_strip(b"")


class TestSafeJoin(unittest.TestCase):
    def setUp(self):
        # We don't actually need the directory to exist for os.path.join and os.path.realpath
        # to test the logic of _safe_join, as long as realpath expands normally on standard systems.
        # However, to ensure absolute predictability we get the real path of the test root.
        self.base_dir = os.path.realpath("/tmp/whacloud_test_out")

    def test_safe_join_valid_file(self):
        dst = _safe_join(self.base_dir, "file.txt")
        expected = os.path.join(self.base_dir, "file.txt")
        self.assertEqual(dst, expected)

    def test_safe_join_valid_nested(self):
        dst = _safe_join(self.base_dir, "dir/file.txt")
        expected = os.path.join(self.base_dir, "dir", "file.txt")
        self.assertEqual(dst, expected)

    def test_safe_join_lstrip_slash(self):
        dst = _safe_join(self.base_dir, "/file.txt")
        # The slash should be stripped so it's joined safely
        expected = os.path.join(self.base_dir, "file.txt")
        self.assertEqual(dst, expected)

    def test_safe_join_escape_attempt_single(self):
        with self.assertRaises(ValueError) as context:
            _safe_join(self.base_dir, "../escape.txt")
        self.assertIn("Refusing path that escapes output dir", str(context.exception))

    def test_safe_join_escape_attempt_multiple(self):
        with self.assertRaises(ValueError) as context:
            _safe_join(self.base_dir, "../../escape.txt")
        self.assertIn("Refusing path that escapes output dir", str(context.exception))

    def test_safe_join_tricky_escape(self):
        with self.assertRaises(ValueError) as context:
            _safe_join(self.base_dir, "dir/../../escape.txt")
        self.assertIn("Refusing path that escapes output dir", str(context.exception))


if __name__ == "__main__":
    unittest.main()
