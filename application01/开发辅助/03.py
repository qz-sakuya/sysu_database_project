def creat_del_station_cmd(station_list, line, no_start, reverse=True):
    for station in station_list:
        cmd_str = "python manage.py delete_data delete_platform \"{}\" \"{}\"".format(line, station)
        print(cmd_str)


stations = [
    "黄村", "车陂", "车陂南", "万胜围", "官洲", "大学城北", "大学城南", "新造", "石碁",
    "低涌", "东涌", "庆盛", "黄阁汽车城", "黄阁", "蕉门", "金洲", "飞沙角",
    "广隆", "大涌", "塘坑", "南横", "南沙客运港"
]

if __name__ == '__main__':
    # 记得改线路号！！！！！！！！！！！！！
    creat_del_station_cmd(stations, '3号线北延段', 1, True)
