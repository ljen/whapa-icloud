import unittest
from libs.whapa import size_file

class TestWhapa(unittest.TestCase):
    def test_size_file(self):
        # Edge cases and values in KB
        self.assertEqual(size_file(0), "(0.00 KB)")
        self.assertEqual(size_file(1024), "(1.00 KB)")
        self.assertEqual(size_file(1048576), "(1024.00 KB)")

        # Values in MB
        self.assertEqual(size_file(1048577), "(1.00 MB)")
        self.assertEqual(size_file(2097152), "(2.00 MB)")

if __name__ == "__main__":
    unittest.main()
