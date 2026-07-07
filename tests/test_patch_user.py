import unittest
from unittest.mock import patch, mock_open
import importlib.util
import sys
import os

class TestPatchUser(unittest.TestCase):

    def test_patch_user_match(self):
        old_text = (
            "                        if args.user_all or (i == args.user):\n"
            "                            if i.split('@')[1] == 's.whatsapp.net':\n"
            "                                report_html = \"report_user_chat_\" + i.split('@')[0] + \".html\"\n"
            "                            sql_string_copy += \" AND messages.key_remote_jid LIKE '%\" + i + \"%'\"\n"
            "                            sql_count_copy += \" AND messages.key_remote_jid LIKE '%\" + i + \"%'\"\n"
            "                            arg_group = \"\"\n"
            "                            arg_user = i.split('@')[0]"
        )

        expected_text = (
            "                        if args.user_all or (i == args.user):\n"
            "                            i_split = i.split('@')\n"
            "                            if len(i_split) >= 2 and i_split[1] == 's.whatsapp.net':\n"
            "                                report_html = \"report_user_chat_\" + i_split[0] + \".html\"\n"
            "                            sql_string_copy += \" AND messages.key_remote_jid LIKE '%\" + i + \"%'\"\n"
            "                            sql_count_copy += \" AND messages.key_remote_jid LIKE '%\" + i + \"%'\"\n"
            "                            arg_group = \"\"\n"
            "                            arg_user = i_split[0] if len(i_split) >= 2 else i"
        )

        m = mock_open(read_data=old_text)

        with patch('builtins.open', m):
            with patch('builtins.print') as mock_print:
                spec = importlib.util.spec_from_file_location("patch_user", "patch_user.py")
                patch_user_mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(patch_user_mod)

                m.assert_any_call("libs/whapa.py", "r", newline="")
                m.assert_any_call("libs/whapa.py", "w", newline="")

                handle = m()
                handle.write.assert_called_once_with(expected_text)
                mock_print.assert_called_once_with("Replaced 1 occurrences")

    def test_patch_user_no_match(self):
        no_match_text = "Some random text that does not match the pattern."
        m = mock_open(read_data=no_match_text)

        with patch('builtins.open', m):
            with patch('builtins.print') as mock_print:
                spec = importlib.util.spec_from_file_location("patch_user", "patch_user.py")
                patch_user_mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(patch_user_mod)

                m.assert_called_once_with("libs/whapa.py", "r", newline="")
                handle = m()
                handle.write.assert_not_called()
                mock_print.assert_called_once_with("Replaced 0 occurrences")

    def test_patch_user_crlf(self):
        old_text = (
            "                        if args.user_all or (i == args.user):\r\n"
            "                            if i.split('@')[1] == 's.whatsapp.net':\r\n"
            "                                report_html = \"report_user_chat_\" + i.split('@')[0] + \".html\"\r\n"
            "                            sql_string_copy += \" AND messages.key_remote_jid LIKE '%\" + i + \"%'\"\r\n"
            "                            sql_count_copy += \" AND messages.key_remote_jid LIKE '%\" + i + \"%'\"\r\n"
            "                            arg_group = \"\"\r\n"
            "                            arg_user = i.split('@')[0]"
        )

        expected_text = (
            "                        if args.user_all or (i == args.user):\n"
            "                            i_split = i.split('@')\n"
            "                            if len(i_split) >= 2 and i_split[1] == 's.whatsapp.net':\n"
            "                                report_html = \"report_user_chat_\" + i_split[0] + \".html\"\n"
            "                            sql_string_copy += \" AND messages.key_remote_jid LIKE '%\" + i + \"%'\"\n"
            "                            sql_count_copy += \" AND messages.key_remote_jid LIKE '%\" + i + \"%'\"\n"
            "                            arg_group = \"\"\n"
            "                            arg_user = i_split[0] if len(i_split) >= 2 else i"
        )

        m = mock_open(read_data=old_text)

        with patch('builtins.open', m):
            with patch('builtins.print') as mock_print:
                spec = importlib.util.spec_from_file_location("patch_user", "patch_user.py")
                patch_user_mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(patch_user_mod)

                handle = m()
                handle.write.assert_called_once_with(expected_text)
                mock_print.assert_called_once_with("Replaced 1 occurrences")

if __name__ == '__main__':
    unittest.main()
