import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'libs')))
from whachat import startsWithDateTimeiOS

class TestWhachat(unittest.TestCase):
    def test_startsWithDateTimeiOS_valid(self):
        # Test basic format
        self.assertTrue(startsWithDateTimeiOS("[25/8/20, 19:52:23] Jordi: Hello"))
        # Test with dots
        self.assertTrue(startsWithDateTimeiOS("[25.08.20, 19:52:23] Jordi: Hello"))
        # Test without comma
        self.assertTrue(startsWithDateTimeiOS("[25/8/20 10:02:14] Jordi: Hello"))
        # Test without message part
        self.assertTrue(startsWithDateTimeiOS("[25/8/20, 19:52:23] "))
        # Test valid matching behavior based on current regex
        self.assertTrue(startsWithDateTimeiOS("[25/8/20] Jordi: Hello"))
        self.assertTrue(startsWithDateTimeiOS("[25/8/20,] Jordi: Hello"))

    def test_startsWithDateTimeiOS_invalid(self):
        # Missing bracket
        self.assertFalse(startsWithDateTimeiOS("25/8/20, 19:52:23]"))
        self.assertFalse(startsWithDateTimeiOS("[25/8/20, 19:52:23"))
        # Missing both brackets
        self.assertFalse(startsWithDateTimeiOS("25/8/20, 19:52:23"))
        # Completely invalid
        self.assertFalse(startsWithDateTimeiOS("Hello world"))
        self.assertFalse(startsWithDateTimeiOS("[]"))
        # Invalid date format (alphabetic)
        self.assertFalse(startsWithDateTimeiOS("[a/b/c, 19:52:23] Jordi: Hello"))

    def test_startsWithDateTimeiOS_edge_cases(self):
        # Empty string
        self.assertFalse(startsWithDateTimeiOS(""))
        # Only brackets
        self.assertFalse(startsWithDateTimeiOS("[]"))
        # Multiple brackets
        self.assertTrue(startsWithDateTimeiOS("[25/8/20, 19:52:23] [Jordi]: Hello"))

if __name__ == '__main__':
    unittest.main()
