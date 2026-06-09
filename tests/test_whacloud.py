import unittest
from libs.whacloud import _pkcs7_strip

class TestPkcs7Strip(unittest.TestCase):
    def test_valid_padding(self):
        # Test valid padding lengths from 1 to 16
        base_data = b"hello_world"
        for i in range(1, 17):
            padded_data = base_data + bytes([i]) * i
            self.assertEqual(_pkcs7_strip(padded_data), base_data)

    def test_invalid_padding_value(self):
        # Padding values must be between 1 and 16
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

if __name__ == '__main__':
    unittest.main()
