import re

with open("libs/whapa.py", "r", newline="") as f:
    content = f.read()


def replace_split(match):
    return """                        if args.user_all or (i == args.user):
                            i_split = i.split('@')
                            if len(i_split) >= 2 and i_split[1] == 's.whatsapp.net':
                                report_html = "report_user_chat_" + i_split[0] + ".html"
                            sql_string_copy += " AND messages.key_remote_jid LIKE '%" + i + "%'"
                            sql_count_copy += " AND messages.key_remote_jid LIKE '%" + i + "%'"
                            arg_group = ""
                            arg_user = i_split[0] if len(i_split) >= 2 else i"""


pattern = r"                        if args.user_all or \(i == args.user\):\r?\n                            if i.split\('@'\)\[1\] == 's.whatsapp.net':\r?\n                                report_html = \"report_user_chat_\" \+ i.split\('@'\)\[0\] \+ \".html\"\r?\n                            sql_string_copy \+= \" AND messages.key_remote_jid LIKE '%\" \+ i \+ \"%'\"\r?\n                            sql_count_copy \+= \" AND messages.key_remote_jid LIKE '%\" \+ i \+ \"%'\"\r?\n                            arg_group = \"\"\r?\n                            arg_user = i.split\('@'\)\[0\]"

new_content, count = re.subn(pattern, replace_split, content, flags=re.DOTALL)
print(f"Replaced {count} occurrences")

if count > 0:
    with open("libs/whapa.py", "w", newline="") as f:
        f.write(new_content)
