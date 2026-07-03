import unittest
from libs.whachat import (
    startsWithDateTimeAndroid,
    startsWithDateTimeiOS,
    getDataPointiOS,
    getDataPointAndroid,
)


def test_startsWithDateTimeAndroid_valid():
    assert startsWithDateTimeAndroid("24/5/18 14:25 - Sergio F: No se tío")
    assert startsWithDateTimeAndroid("24.07.21, 10:15 - Hello")
    assert startsWithDateTimeAndroid("12/12/2021 14:25 - Hey")
    assert startsWithDateTimeAndroid("1/1/20 1:2:3 - Msg")
    assert startsWithDateTimeAndroid("24/5/18 14:25 -")


def test_startsWithDateTimeAndroid_invalid():
    assert not startsWithDateTimeAndroid("Not a date - Hello")
    assert not startsWithDateTimeAndroid("24/5/18 14:25")
    assert not startsWithDateTimeAndroid("")
    assert not startsWithDateTimeAndroid("Sergio F: No se tío")


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
        self.assertEqual(
            message,
            "Messages to this group are now secured with end-to-end encryption.",
        )

    def test_phone_number_author(self):
        line = "[25/8/20, 10:02:14] +34 666 555 444: Hello"
        date, time, author, message = getDataPointiOS(line)
        self.assertEqual(date, "25/8/20")
        self.assertEqual(time, "10:02:14")
        self.assertEqual(author, "+34 666 555 444")
        self.assertEqual(message, "Hello")


class TestGetDataPointAndroid(unittest.TestCase):
    def test_english_format(self):
        line = "23/5/18 15:24 - Sergio F: No se tío no le preguntao al final"
        date, time, author, message = getDataPointAndroid(line)
        self.assertEqual(date, "23/5/18")
        self.assertEqual(time, "15:24")
        self.assertEqual(author, "Sergio F")
        self.assertEqual(message, "No se tío no le preguntao al final")

    def test_unknown_mobile_format(self):
        line = "24.07.21, 10:15 - Jordi Subinspector: Hola"
        date, time, author, message = getDataPointAndroid(line)
        self.assertEqual(date, "24.07.21")
        self.assertEqual(time, "10:15")
        self.assertEqual(author, "Jordi Subinspector")
        self.assertEqual(message, "Hola")

    def test_no_author(self):
        line = "25/8/20 10:02 - Messages to this group are now secured with end-to-end encryption."
        date, time, author, message = getDataPointAndroid(line)
        self.assertEqual(date, "25/8/20")
        self.assertEqual(time, "10:02")
        self.assertIsNone(author)
        self.assertEqual(
            message,
            "Messages to this group are now secured with end-to-end encryption.",
        )

    def test_phone_number_author(self):
        line = "25/8/20 10:02 - +34 666 555 444: Hello"
        date, time, author, message = getDataPointAndroid(line)
        self.assertEqual(date, "25/8/20")
        self.assertEqual(time, "10:02")
        self.assertEqual(author, "+34 666 555 444")
        self.assertEqual(message, "Hello")


class TestParticipantsColor(unittest.TestCase):
    def setUp(self):
        # Clear the global color dictionary before each test
        import libs.whachat
        libs.whachat.color.clear()

    def test_participants_color_empty(self):
        from libs.whachat import participants_color
        import libs.whachat

        result = participants_color([])
        self.assertEqual(result, {})
        self.assertEqual(libs.whachat.color, {})

    def test_participants_color_assignment(self):
        from libs.whachat import participants_color
        import libs.whachat

        users = ["alice", "bob", "charlie"]
        result = participants_color(users)

        expected_colors = [
            "#FF0000", "#000000", "#5586e5", "#800000",
            "#00008B", "#006400", "#800080", "#8B4513",
            "#FF4500", "#2F4F4F", "#DC143C", "#696969",
            "#008B8B", "#D2691E", "#CD5C5C", "#4682B4",
        ]

        self.assertEqual(len(result), 3)
        for user in users:
            self.assertIn(user, result)
            self.assertIn(result[user], expected_colors)

        # Check global state
        self.assertEqual(libs.whachat.color, result)

    def test_participants_color_preserves_existing(self):
        from libs.whachat import participants_color
        import libs.whachat

        libs.whachat.color["existing_user"] = "#123456"
        users = ["new_user"]
        result = participants_color(users)

        self.assertIn("existing_user", result)
        self.assertEqual(result["existing_user"], "#123456")
        self.assertIn("new_user", result)
        self.assertEqual(len(result), 2)


if __name__ == "__main__":
    unittest.main()
