import unittest
import os
import sys
import sqlite3
import tempfile
import shutil
from unittest.mock import patch

# Add the parent directory to the path so we can import libs
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from libs.whamerge import (
    merge,
    merge_win,
    messages_columns,
    chatlist_columns,
    quote_columns,
    thumbnail_columns,
)


class TestWhamerge(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db1_path = os.path.join(self.test_dir, "db1.db")
        self.db2_path = os.path.join(self.test_dir, "db2.db")
        self.output_db = os.path.join(self.test_dir, "output.db")

        self.create_test_db(self.db1_path, [1, 2], [10, 20], [100, 200], [1000, 2000])
        self.create_test_db(self.db2_path, [2, 3], [20, 30], [200, 300], [2000, 3000])

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def create_test_db(self, path, msg_ids, chat_ids, quote_ids, thumb_ids):
        with sqlite3.connect(path) as conn:
            cursor = conn.cursor()
            # Create tables
            cursor.execute(f"CREATE TABLE messages ({','.join(messages_columns)});")
            cursor.execute(f"CREATE TABLE chat ({','.join(chatlist_columns)});")
            cursor.execute(f"CREATE TABLE messages_quotes ({','.join(quote_columns)});")
            cursor.execute(
                f"CREATE TABLE message_thumbnails ({','.join(thumbnail_columns)}, rowid INTEGER PRIMARY KEY);"
            )

            # Insert dummy data
            for msg_id in msg_ids:
                vals = [msg_id] + [str(msg_id)] * (len(messages_columns) - 1)
                cursor.execute(
                    f"INSERT INTO messages VALUES ({','.join(['?'] * len(messages_columns))})",
                    vals,
                )

            for chat_id in chat_ids:
                vals = [chat_id] + [str(chat_id)] * (len(chatlist_columns) - 1)
                cursor.execute(
                    f"INSERT INTO chat VALUES ({','.join(['?'] * len(chatlist_columns))})",
                    vals,
                )

            for quote_id in quote_ids:
                vals = [quote_id] + [str(quote_id)] * (len(quote_columns) - 1)
                cursor.execute(
                    f"INSERT INTO messages_quotes VALUES ({','.join(['?'] * len(quote_columns))})",
                    vals,
                )

            for thumb_id in thumb_ids:
                # Store thumb_id in the first column ('thumbnail') as string to track it
                vals = (
                    [str(thumb_id)] + [""] * (len(thumbnail_columns) - 1) + [thumb_id]
                )
                cursor.execute(
                    f"INSERT INTO message_thumbnails VALUES ({','.join(['?'] * (len(thumbnail_columns) + 1))})",
                    vals,
                )

            conn.commit()

    @patch("builtins.print")
    def test_merge_success(self, mock_print):
        # merge appends an output file if > 2 databases exist in path
        db_path = self.test_dir + os.sep

        merge(db_path, self.output_db)

        # Verify the output db contains merged data (unique IDs: 1, 2, 3)
        with sqlite3.connect(self.output_db) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT _id FROM messages")
            msg_ids = sorted([row[0] for row in cursor.fetchall()])
            self.assertEqual(msg_ids, [1, 2, 3])

            cursor.execute("SELECT _id FROM chat")
            chat_ids = sorted([row[0] for row in cursor.fetchall()])
            self.assertEqual(chat_ids, [10, 20, 30])

            cursor.execute("SELECT _id FROM messages_quotes")
            quote_ids = sorted([row[0] for row in cursor.fetchall()])
            self.assertEqual(quote_ids, [100, 200, 300])

            cursor.execute("SELECT thumbnail FROM message_thumbnails")
            thumb_ids = sorted([int(row[0]) for row in cursor.fetchall()])
            self.assertEqual(thumb_ids, [1000, 2000, 3000])

    @patch("builtins.print")
    def test_merge_win_success(self, mock_print):
        db_path = self.test_dir + os.sep

        merge_win(db_path, self.output_db)

        # Verify the output db contains merged data (unique IDs: 1, 2, 3)
        with sqlite3.connect(self.output_db) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT _id FROM messages")
            msg_ids = sorted([row[0] for row in cursor.fetchall()])
            self.assertEqual(msg_ids, [1, 2, 3])

    @patch("builtins.print")
    def test_merge_no_dbs(self, mock_print):
        # Create an empty directory
        empty_dir = tempfile.mkdtemp()
        try:
            with self.assertRaises(SystemExit):
                merge(empty_dir + os.sep, os.path.join(empty_dir, "output.db"))
        finally:
            shutil.rmtree(empty_dir)

    @patch("builtins.print")
    def test_merge_one_db(self, mock_print):
        # Directory with only one db
        one_db_dir = tempfile.mkdtemp()
        try:
            self.create_test_db(
                os.path.join(one_db_dir, "single.db"), [1], [1], [1], [1]
            )
            with self.assertRaises(SystemExit):
                merge(one_db_dir + os.sep, os.path.join(one_db_dir, "output.db"))
        finally:
            shutil.rmtree(one_db_dir)

    @patch("builtins.print")
    @patch("libs.whamerge.shutil.copy")
    def test_merge_copy_error(self, mock_copy, mock_print):
        mock_copy.side_effect = Exception("Mocked copy error")
        db_path = self.test_dir + os.sep

        try:
            merge(db_path, self.output_db)
        except sqlite3.OperationalError:
            # We expect an operational error since copy fails, meaning the db is not created,
            # but whamerge attempts to connect to it right after
            pass

        mock_print.assert_any_call("[e] Error copying: ", mock_copy.side_effect)

    @patch("builtins.print")
    @patch("libs.whamerge.shutil.copy")
    def test_merge_win_copy_error(self, mock_copy, mock_print):
        mock_copy.side_effect = Exception("Mocked copy error")
        db_path = self.test_dir + os.sep

        try:
            merge_win(db_path, self.output_db)
        except sqlite3.OperationalError:
            pass

        mock_print.assert_any_call("[e] Error copying: ", mock_copy.side_effect)


if __name__ == "__main__":
    unittest.main()
