import pytest
import sqlite3
import os
import sys

# Pre-requisites path adjustment as requested in memories
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import libs.whamerge as whamerge

def create_db(name, messages):
    conn = sqlite3.connect(name)
    c = conn.cursor()
    c.execute('CREATE TABLE messages (_id INTEGER PRIMARY KEY, key_remote_jid TEXT, key_from_me INTEGER, key_id TEXT, status INTEGER, needs_push INTEGER, data TEXT, timestamp INTEGER, media_url TEXT, media_mime_type TEXT, media_wa_type INTEGER, media_size INTEGER, media_name TEXT, media_caption TEXT, media_hash TEXT, media_duration INTEGER, origin INTEGER, latitude REAL, longitude REAL, thumb_image TEXT, remote_resource TEXT, received_timestamp INTEGER, send_timestamp INTEGER, receipt_server_timestamp INTEGER, receipt_device_timestamp INTEGER, read_device_timestamp INTEGER, played_device_timestamp INTEGER, raw_data BLOB, recipient_count INTEGER, participant_hash TEXT, starred INTEGER, quoted_row_id INTEGER, mentioned_jids TEXT, multicast_id TEXT, edit_version INTEGER, media_enc_hash TEXT, payment_transaction_id TEXT, forwarded INTEGER, preview_type INTEGER, send_count INTEGER, lookup_tables INTEGER, future_message_type INTEGER, message_add_on_flags INTEGER)')
    c.execute('CREATE TABLE chat (_id INTEGER PRIMARY KEY, jid_row_id INTEGER, hidden INTEGER, subject TEXT, created_timestamp INTEGER, display_message_row_id INTEGER, last_message_row_id INTEGER, last_read_message_row_id INTEGER, last_read_receipt_sent_message_row_id INTEGER, last_important_message_row_id INTEGER, archived INTEGER, sort_timestamp INTEGER, mod_tag INTEGER, gen INTEGER, spam_detection INTEGER, unseen_earliest_message_received_time INTEGER, unseen_message_count INTEGER, unseen_missed_calls_count INTEGER, unseen_row_count INTEGER, plaintext_disabled INTEGER, vcard_ui_dismissed INTEGER, change_number_notified_message_row_id INTEGER, show_group_description INTEGER, ephemeral_expiration INTEGER, last_read_ephemeral_message_row_id INTEGER, ephemeral_setting_timestamp INTEGER, unseen_important_message_count INTEGER, ephemeral_disappearing_messages_initiator INTEGER, group_type INTEGER, last_message_reaction_row_id INTEGER, last_seen_message_reaction_row_id INTEGER, unseen_message_reaction_count INTEGER, growth_lock_level INTEGER, growth_lock_expiration_ts INTEGER, last_read_message_sort_id INTEGER, display_message_sort_id INTEGER, last_message_sort_id INTEGER, last_read_receipt_sent_message_sort_id INTEGER)')
    c.execute('CREATE TABLE messages_quotes (_id INTEGER PRIMARY KEY, key_remote_jid TEXT, key_from_me INTEGER, key_id TEXT, status INTEGER, needs_push INTEGER, data TEXT, timestamp INTEGER, media_url TEXT, media_mime_type TEXT, media_wa_type INTEGER, media_size INTEGER, media_name TEXT, media_caption TEXT, media_hash TEXT, media_duration INTEGER, origin INTEGER, latitude REAL, longitude REAL, thumb_image TEXT, remote_resource TEXT, received_timestamp INTEGER, send_timestamp INTEGER, receipt_server_timestamp INTEGER, receipt_device_timestamp INTEGER, read_device_timestamp INTEGER, played_device_timestamp INTEGER, raw_data BLOB, recipient_count INTEGER, participant_hash TEXT, starred INTEGER, quoted_row_id INTEGER, mentioned_jids TEXT, multicast_id TEXT, edit_version INTEGER, media_enc_hash TEXT, payment_transaction_id TEXT, forwarded INTEGER, preview_type INTEGER, send_count INTEGER, lookup_tables INTEGER, future_message_type INTEGER, message_add_on_flags INTEGER)')
    c.execute('CREATE TABLE message_thumbnails (rowid INTEGER PRIMARY KEY, thumbnail BLOB, timestamp INTEGER, key_remote_jid TEXT, key_from_me INTEGER, key_id TEXT)')

    # We will just pad columns with None to match the schema
    m_pad = [None] * (len(whamerge.messages_columns) - 2)
    c_pad = [None] * (len(whamerge.chatlist_columns) - 2)
    q_pad = [None] * (len(whamerge.quote_columns) - 2)

    # Message thumbnails has 5 columns + rowid
    t_pad = [None] * 4

    for i in messages:
        c.execute('INSERT INTO messages VALUES (?, ?' + ', ?'*len(m_pad) + ')', (i, f'msg{i}', *m_pad))
        c.execute('INSERT INTO chat VALUES (?, ?' + ', ?'*len(c_pad) + ')', (i, f'chat{i}', *c_pad))
        c.execute('INSERT INTO messages_quotes VALUES (?, ?' + ', ?'*len(q_pad) + ')', (i, f'quote{i}', *q_pad))
        c.execute('INSERT INTO message_thumbnails VALUES (?, ?' + ', ?'*len(t_pad) + ')', (i, b'thumb', *t_pad))

    conn.commit()
    conn.close()


def test_merge(tmp_path, monkeypatch):
    """Test functionality of merge."""

    db_dir = tmp_path / "dbs"
    db_dir.mkdir()

    db1_path = str(db_dir / "db1.db")
    db2_path = str(db_dir / "db2.db")

    # DB1 has 1, 2, 3
    create_db(db1_path, [1, 2, 3])
    # DB2 has 2, 3, 4
    create_db(db2_path, [2, 3, 4])

    out_db = str(tmp_path / "msgstore_merge.db")

    class Args:
        path = str(db_dir) + '/'

    whamerge.args = Args()

    try:
        whamerge.merge(str(db_dir) + '/', out_db)
    except SystemExit:
        pass

    # Check if out_db has 1, 2, 3, 4
    conn = sqlite3.connect(out_db)
    c = conn.cursor()
    c.execute("SELECT _id FROM messages ORDER BY _id")
    ids = c.fetchall()
    conn.close()

    assert [i[0] for i in ids] == [1, 2, 3, 4]
