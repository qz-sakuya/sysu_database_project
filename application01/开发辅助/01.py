def creat_train_cmd(train_list, line, up_first):
    for train in train_list:
        station = train[0]
        time_list = train[1:]
        type_list = ["first", "first", 'last', 'last']
        up_list = ["up", 'down', "up", 'down']
        if not up_first:
            up_list = ['down', "up", 'down', "up"]
        for index, time in enumerate(time_list):
            if time != '--':
                cmd_str = "python manage.py add_data add_{}_train \"{}\" \"{}\" {} {}".format(type_list[index], line,
                                                                                              station,
                                                                                              up_list[index], time)
                print(cmd_str)


def creat_train_cmd_2(train_list, line, up_first):
    for train in train_list:
        station = train[0]
        time_list = train[1:]
        type_list = ["first", 'last',"first", 'last']
        up_list = ["up", "up", 'down', 'down']
        if not up_first:
            up_list = ['down', 'down', "up", "up"]
        for index, time in enumerate(time_list):
            if time != '——':
                cmd_str = "python manage.py add_data add_{}_train \"{}\" \"{}\" {} {}".format(type_list[index], line,
                                                                                              station,
                                                                                              up_list[index], time)
                print(cmd_str)


train_data =stations_schedule = schedule = [
    ["新城东", "06:00", "--", "22:30", "--"],
    ["东平", "06:02", "06:27", "22:32", "23:56"],
    ["世纪莲", "06:04", "06:25", "22:34", "23:53"],
    ["澜石", "06:08", "06:21", "22:38", "23:49"],
    ["魁奇路", "06:00", "06:19", "22:40", "23:47"],
    ["季华园", "06:01", "06:16", "22:41", "23:45"],
    ["同济路", "06:03", "06:14", "22:43", "23:42"],
    ["祖庙", "06:05", "06:11", "22:46", "23:40"],
    ["普君北路", "06:08", "06:10", "22:48", "23:38"],
    ["朝安", "06:10", "06:07", "22:50", "23:36"],
    ["桂城", "06:12", "06:05", "22:52", "23:33"],
    ["南桂路", "06:14", "06:03", "22:54", "23:31"],
    ["岗", "06:16", "06:23", "22:56", "23:29"],
    ["千灯湖", "06:18", "06:21", "22:59", "23:26"],
    ["金融高新区", "06:00", "06:19", "23:01", "23:24"],
    ["龙溪", "06:04", "06:14", "23:05", "23:20"],
    ["菊树", "06:07", "06:12", "23:08", "23:17"],
    ["西塱", "06:10", "06:10", "23:11", "23:15"],
    ["鹤洞", "06:12", "06:15", "23:13", "23:13"],
    ["沙涌", "06:14", "06:12", "23:16", "23:10"],
    ["沙园", "06:17", "06:10", "23:19", "23:08"],
    ["燕岗", "06:20", "06:07", "23:22", "23:06"],
    ["石溪", "06:22", "06:05", "23:25", "23:05"],
    ["南洲", "06:25", "06:02", "23:27", "23:02"],
    ["沥滘", "--", "06:00", "--", "23:00"]
]
if __name__ == '__main__':
    # 记得改线路号！！！！！！！！！！！！！
    creat_train_cmd(train_data, '广佛线', up_first=True)
