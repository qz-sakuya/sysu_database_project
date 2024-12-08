def creat_station_cmd(station_list, line, no_start, reverse=True, skip = None):
    if reverse:
        station_list = station_list[::-1]
    for station in station_list:
        cmd_str = "python manage.py add_data add_station \"{}\" ".format(station)
        print(cmd_str)

    print(' ')
    no = no_start
    for station in station_list:
        cmd_str = "python manage.py add_data add_platform \"{}\" {} \"{}\"".format(line, no, station)
        print(cmd_str)
        no += 1
        if no == 0 or no in skip:  # 官方编号中没有0
            no += 1

    print(' ')
    section_no = 1
    for i in range(len(station_list) - 1):
        cmd_str = "python manage.py add_data add_section \"{}\" {} \"{}\" \"{}\" 2 1".format(line, section_no,
                                                                                             station_list[i],
                                                                                             station_list[i + 1])
        print(cmd_str)
        section_no += 1

stations = [
    "黄村", "车陂", "车陂南", "万胜围", "官洲", "大学城北", "大学城南", "新造", "石碁",
    "海傍", "低涌", "东涌", "庆盛", "黄阁汽车城", "黄阁", "蕉门", "金洲", "飞沙角",
    "广隆", "大涌", "塘坑", "南横", "南沙客运港"
]

if __name__ == '__main__':
    # 记得改线路号！！！！！！！！！！！！！
    creat_station_cmd(stations, '4号线', 1, True, skip=[16])
