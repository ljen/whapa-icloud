import unittest
from libs.whachat import startsWithDateTimeiOS, getDataPointiOS

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

class TestGetDataPointiOS(unittest.TestCase):
    def test_english_format(self):
        line = "[25/8/20, 10:02:14] Jordi Subinspector Tecnologicos: Por qué no vieron los maniquiey"
        date, time, author, message = getDataPointiOS(line)
        self.assertEqual(date, "25/8/20")
        self.assertEqual(time, "10:02:14")
        self.assertEqual(author, "Jordi Subinspector Tecnologicos")
        self.assertEqual(message, "Por qué no vieron los maniquiey")

    def test_spanish_format(self):
        line = "[25/8/20 10:02:14] Jordi Subinspector: Hola"
        date, time, author, message = getDataPointiOS(line)
        self.assertEqual(date, "25/8/20")
        self.assertEqual(time, "10:02:14")
        self.assertEqual(author, "Jordi Subinspector")
        self.assertEqual(message, "Hola")

    def test_no_author(self):
        line = "[25/8/20, 10:02:14] Messages to this group are now secured with end-to-end encryption."
        date, time, author, message = getDataPointiOS(line)
        self.assertEqual(date, "25/8/20")
        self.assertEqual(time, "10:02:14")
        self.assertIsNone(author)
        self.assertEqual(message, "Messages to this group are now secured with end-to-end encryption.")

    def test_phone_number_author(self):
        line = "[25/8/20, 10:02:14] +34 666 555 444: Hello"
        date, time, author, message = getDataPointiOS(line)
        self.assertEqual(date, "25/8/20")
        self.assertEqual(time, "10:02:14")
        self.assertEqual(author, "+34 666 555 444")
        self.assertEqual(message, "Hello")

if __name__ == '__main__':
    unittest.main()
