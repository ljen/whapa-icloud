import unittest
import os
import sys

# Add the parent directory to the path so we can import libs
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from libs.whacloud import _safe_join

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

if __name__ == '__main__':
    unittest.main()
