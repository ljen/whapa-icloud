  4080	                " messages.remote_resource, messages.edit_version, messages.thumb_image, messages.recipient_count, messages.raw_data, messages.starred, messages.quoted_row_id, "
  4081	                " message_thumbnails.thumbnail, messages._id, messages.forwarded  FROM messages LEFT JOIN message_thumbnails ON messages.key_id = message_thumbnails.key_id WHERE messages.timestamp BETWEEN '"
  4082	            )
  4083	            sql_count = "SELECT COUNT(*) FROM messages LEFT JOIN message_thumbnails ON messages.key_id = message_thumbnails.key_id WHERE messages.timestamp BETWEEN '"
  4084	            try:
  4085	                epoch_start = "0"
  4086	                """ current date in Epoch milliseconds string """
  4087	                epoch_end = str(
  4088	                    1000
  4089	                    * int(
  4090	                        time.mktime(
  4091	                            time.strptime(
  4092	                                time.strftime("%d-%m-%Y %H:%M"), "%d-%m-%Y %H:%M"
  4093	                            )
  4094	                        )
  4095	                    )
  4096	                )
  4097
  4098	                if args.time_start:
  4099	                    epoch_start = 1000 * int(
  4100	                        time.mktime(time.strptime(args.time_start, "%d-%m-%Y %H:%M"))
  4101	                    )
  4102	                if args.time_end:
  4103	                    epoch_end = 1000 * int(
  4104	                        time.mktime(time.strptime(args.time_end, "%d-%m-%Y %H:%M"))
  4105	                    )
  4106	                sql_string += str(epoch_start) + "' AND '" + str(epoch_end) + "'"
  4107	                sql_count += str(epoch_start) + "' AND '" + str(epoch_end) + "'"
  4108
  4109	                if args.output:
  4110	                    local = args.output
  4111	                else:
  4112	                    local = os.getcwd() + "/"
  4113
  4114	                if args.text:
  4115	                    sql_string += " AND messages.data LIKE '%" + str(args.text) + "%'"
  4116	                    sql_count += " AND messages.data LIKE '%" + str(args.text) + "%'"
  4117	                if args.web:
  4118	                    sql_string += " AND messages.key_id LIKE '3EB0%'"
  4119	                    sql_count += " AND messages.key_id LIKE '3EB0%'"
  4120	                if args.starred:
  4121	                    sql_string += " AND messages.starred = 1"
  4122	                    sql_count += " AND messages.starred = 1"
  4123	                if args.broadcast:
  4124	                    sql_string += " AND messages.remote_resource LIKE '%broadcast%'"
  4125	                    sql_count += " AND messages.remote_resource LIKE '%broadcast%'"
  4126	                if args.report:
  4127	                    report_var = args.report
  4128	                    get_configs()
  4129	                if args.type_text:
  4130	                    sql_string += " AND messages.media_wa_type = 0"
  4131	                    sql_count += " AND messages.media_wa_type = 0"
  4132	                if args.type_image:
  4133	                    sql_string += " AND messages.media_wa_type = 1"
  4134	                    sql_count += " AND messages.media_wa_type = 1"
  4135	                if args.type_audio:
  4136	                    sql_string += " AND messages.media_wa_type = 2"
  4137	                    sql_count += " AND messages.media_wa_type = 2"
  4138	                if args.type_video:
  4139	                    sql_string += " AND messages.media_wa_type = 3"
  4140	                    sql_count += " AND messages.media_wa_type = 3"
  4141	                if args.type_contact:
  4142	                    sql_string += (
  4143	                        " AND messages.media_wa_type = 4 OR messages.media_wa_type = 14"
  4144	                    )
  4145	                    sql_count += (
  4146	                        " AND messages.media_wa_type = 4 OR messages.media_wa_type = 14"
  4147	                    )
  4148	                if args.type_location:
  4149	                    sql_string += " AND messages.media_wa_type = 5"
  4150	                    sql_count += " AND messages.media_wa_type = 5"
  4151	                if args.type_call:
  4152	                    sql_string += (
  4153	                        " AND messages.media_wa_type = 8 OR messages.media_wa_type = 10"
  4154	                    )
  4155	                    sql_count += (
  4156	                        " AND messages.media_wa_type = 8 OR messages.media_wa_type = 10"
  4157	                    )
  4158	                if args.type_application:
  4159	                    sql_string += " AND messages.media_wa_type = 9"
  4160	                    sql_count += " AND messages.media_wa_type = 9"
  4161	                if args.type_gif:
  4162	                    sql_string += " AND messages.media_wa_type = 13"
  4163	                    sql_count += " AND messages.media_wa_type = 13"
  4164	                if args.type_deleted:
  4165	                    sql_string += " AND messages.media_wa_type = 15"
  4166	                    sql_count += " AND messages.media_wa_type = 15"
  4167	                if args.type_share:
  4168	                    sql_string += " AND messages.media_wa_type = 16"
  4169	                    sql_count += " AND messages.media_wa_type = 16"
  4170	                if args.type_stickers:
  4171	                    sql_string += " AND messages.media_wa_type = 20"
  4172	                    sql_count += " AND messages.media_wa_type = 20"
  4173	                if args.type_system:
  4174	                    sql_string += (
  4175	                        " AND messages.media_wa_type = 0 AND messages.status = 6"
  4176	                    )
  4177	                    sql_count += (
  4178	                        " AND messages.media_wa_type = 0 AND messages.status = 6"
  4179	                    )
  4180
  4181	                params = []
  4182	                if args.user_all:
  4183	                    sql_string += " AND (messages.key_remote_jid LIKE ? OR messages.remote_resource LIKE ?)"
  4184	                    sql_count += " AND (messages.key_remote_jid LIKE ? OR messages.remote_resource LIKE ?)"
  4185	                    params.extend(
  4186	                        [
  4187	                            "%" + str(args.user_all) + "%@s.whatsapp.net",
  4188	                            "%" + str(args.user_all) + "%",
  4189	                        ]
  4190	                    )
  4191	                    arg_user = args.user_all
  4192	                    report_html = "report_user_all_" + args.user_all + ".html"
  4193
  4194	                elif args.user:
  4195	                    sql_string += " AND messages.key_remote_jid LIKE ?"
  4196	                    sql_count += " AND messages.key_remote_jid LIKE ?"
  4197	                    params.append("%" + str(args.user) + "%@s.whatsapp.net")
  4198	                    report_html = "report_user_chat_" + args.user + ".html"
  4199	                    arg_user = args.user
  4200
  4201	                elif args.group:
  4202	                    sql_string += " AND messages.key_remote_jid LIKE ?"
  4203	                    sql_count += " AND messages.key_remote_jid LIKE ?"
  4204	                    params.append("%" + str(args.group) + "%")
  4205	                    arg_group = args.group
  4206	                    if arg_group.split("@")[1] == "g.us":
  4207	                        report_html = "report_group_chat_" + args.group + ".html"
  4208	                        report_group, color = participants(args.group)
  4209	                    else:
  4210	                        report_html = "report_broadcast_chat_" + args.group + ".html"
  4211	                        report_group, color = participants(args.group)
  4212
  4213	                elif args.all:
  4214	                    get_configs()
  4215	                    sql_string_consult = "SELECT raw_string_jid FROM chat_view ORDER BY sort_timestamp DESC"
  4216	                    sql_consult_chat = cursor.execute(sql_string_consult)
  4217	                    chats_live = []
  4218	                    for i in sql_consult_chat:
  4219	                        chats_live.append(i[0])
  4220	                    report_med = " "
  4221	                    print("Loading data ...")
  4222
  4223	                    sql_count_group = sql_count.replace("SELECT COUNT(*)", "SELECT messages.key_remote_jid, COUNT(*)", 1) + " GROUP BY messages.key_remote_jid"
  4224	                    cursor.execute(sql_count_group)
  4225	                    counts_by_jid = {}
  4226	                    while True:
  4227	                        chunk = cursor.fetchmany(1000)
  4228	                        if not chunk:
  4229	                            break
  4230	                        for row in chunk:
  4231	                            if row[0]:
  4232	                                counts_by_jid[row[0]] = row[1]
  4233
  4234	                    for i in chats_live:
  4235	                        sql_string_copy = sql_string
  4236
  4237	                        chat_count = sum(v for k, v in counts_by_jid.items() if i in k)
  4238
  4239	                        if i.split("@")[1] == "g.us":
  4240	                            if report_var == "EN":
  4241	                                report_html = "report_group_chat_" + i + ".html"
  4242	                                report_med += (
  4243	                                    '<tr><th>Group</th><th><a href="report_group_chat_'
  4244	                                    + i
  4245	                                    + ".html"
  4246	                                    + '" target="_blank"> '
  4247	                                    + i
  4248	                                    + gets_name(i)
  4249	                                    + "</a></th></tr>"
  4250	                                )
  4251	                            elif report_var == "ES":
  4252	                                report_html = "report_group_chat_" + i + ".html"
  4253	                                report_med += (
  4254	                                    '<tr><th>Grupo</th><th><a href="report_group_chat_'
  4255	                                    + i
  4256	                                    + ".html"
  4257	                                    + '" target="_blank"> '
  4258	                                    + i
  4259	                                    + gets_name(i)
  4260	                                    + "</a></th></tr>"
  4261	                                )
  4262	                            sql_string_copy += " AND messages.key_remote_jid LIKE ?"
  4263	                            arg_group = i
  4264	                            arg_user = ""
  4265	                            print("\nNumber of messages: {}".format(str(chat_count)))
  4266	                            print(
  4267	                                Fore.RED
  4268	                                + "--------------------------------------------------------------------------------"
  4269	                                + Fore.RESET
  4270	                            )
  4271	                            print(
  4272	                                Fore.CYAN
  4273	                                + "GROUP CHAT "
  4274	                                + i
  4275	                                + Fore.RESET
  4276	                                + Fore.YELLOW
  4277	                                + gets_name(i)
  4278	                                + Fore.RESET
  4279	                            )
  4280	                            report_group, color = participants(arg_group)
  4281
  4282	                        elif i.split("@")[1] == "s.whatsapp.net":
  4283	                            if report_var == "EN":
  4284	                                report_med += (
  4285	                                    '<tr><th>User</th><th><a href="report_user_chat_'
  4286	                                    + i.split("@")[0]
  4287	                                    + ".html"
  4288	                                    + '" target="_blank"> '
  4289	                                    + i.split("@")[0]
  4290	                                    + gets_name(i)
  4291	                                    + "</a></th></tr>"
  4292	                                )
  4293	                                report_html = (
  4294	                                    "report_user_chat_" + i.split("@")[0] + ".html"
  4295	                                )
  4296	                            elif report_var == "ES":
  4297	                                report_med += (
  4298	                                    '<tr><th>Usuario</th><th><a href="report_user_chat_'
  4299	                                    + i.split("@")[0]
  4300	                                    + ".html"
  4301	                                    + '" target="_blank"> '
  4302	                                    + i.split("@")[0]
  4303	                                    + gets_name(i)
  4304	                                    + "</a></th></tr>"
  4305	                                )
  4306	                                report_html = (
  4307	                                    "report_user_chat_" + i.split("@")[0] + ".html"
  4308	                                )
  4309	                            sql_string_copy += " AND messages.key_remote_jid LIKE ?"
  4310	                            arg_group = ""
  4311	                            arg_user = i.split("@")[0]
  4312	                            print("\nNumber of messages: {}".format(str(chat_count)))
  4313	                            print(
  4314	                                Fore.RED
  4315	                                + "--------------------------------------------------------------------------------"
  4316	                                + Fore.RESET
  4317	                            )
  4318	                            print(
  4319	                                Fore.CYAN
  4320	                                + "USER CHAT "
  4321	                                + arg_user
  4322	                                + Fore.RESET
  4323	                                + Fore.YELLOW
  4324	                                + gets_name(i)
  4325	                                + Fore.RESET
  4326	                            )
  4327	                            report_group = ""
  4328
  4329	                        elif i.split("@")[1] == "broadcast":
  4330	                            if report_var == "EN":
  4331	                                report_med += (
  4332	                                    '<tr><th>Broadcast</th><th><a href="report_broadcast_chat_'
  4333	                                    + i.split("@")[0]
  4334	                                    + ".html"
  4335	                                    + '" target="_blank"> '
  4336	                                    + i
  4337	                                    + gets_name(i)
  4338	                                    + "</a></th></tr>"
  4339	                                )
  4340	                                report_html = (
  4341	                                    "report_broadcast_chat_" + i.split("@")[0] + ".html"
  4342	                                )
  4343	                            elif report_var == "ES":
  4344	                                report_med += (
  4345	                                    '<tr><th>Difusión</th><th><a href="report_broadcast_chat_'
  4346	                                    + i.split("@")[0]
  4347	                                    + ".html"
  4348	                                    + '" target="_blank"> '
  4349	                                    + i
  4350	                                    + gets_name(i)
  4351	                                    + "</a></th></tr>"
  4352	                                )
  4353	                                report_html = (
  4354	                                    "report_broadcast_chat_" + i.split("@")[0] + ".html"
  4355	                                )
  4356	                            sql_string_copy += " AND messages.key_remote_jid LIKE ?"
  4357	                            arg_group = ""
  4358	                            arg_user = i
  4359	                            print("\nNumber of messages: {}".format(str(chat_count)))
  4360	                            print(
  4361	                                Fore.RED
  4362	                                + "--------------------------------------------------------------------------------"
  4363	                                + Fore.RESET
  4364	                            )
  4365	                            print(
  4366	                                Fore.CYAN
  4367	                                + "BROADCAST CHAT "
  4368	                                + i
  4369	                                + Fore.RESET
  4370	                                + Fore.YELLOW
  4371	                                + gets_name(i)
  4372	                                + Fore.RESET
  4373	                            )
  4374	                            report_group, color = participants(arg_user)
  4375
  4376	                        sql_consult = cursor.execute(sql_string_copy, ("%" + i + "%",))
  4377	                        messages(sql_consult, chat_count, report_html, local)
  4378	                        print()
  4379
  4380	                    if args.report:
  4381	                        index_report(report_med, local + "index.html")
  4382	                    print("\n[i] Finished")
  4383	                    exit()
  4384
  4385	                print("Loading data ...")
  4386	                count_params = (
  4387	                    params.copy() if (args.user_all or args.user or args.group) else []
  4388	                )
  4389	                result = cursor.execute(sql_count, tuple(count_params))
  4390	                result = cursor.fetchone()
  4391	                print("Number of messages: {}".format(str(result[0])))
  4392	                sql_consult = cursor.execute(sql_string, tuple(count_params))
  4393	                messages(sql_consult, result[0], report_html, local)
  4394	                print("\n[i] Finished")
  4395
  4396	            except Exception as e:
  4397	                print("Error:", e)
  4398
  4399	        elif args.info:
  4400	            if args.output:
