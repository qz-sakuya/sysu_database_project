def creat_station_cmd(station_list, line, no_start, reverse=True, skip=None):
    if skip is None:
        skip = []
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


stations =stations = [
    "新城东", "东平", "世纪莲", "澜石", "魁奇路", "季华园", "同济路", "祖庙", "普君北路",
    "朝安", "桂城", "南桂路", "岗", "千灯湖", "金融高新区", "龙溪", "菊树", "西塱",
    "鹤洞", "沙涌", "沙园", "燕岗", "石溪", "南洲", "沥滘"
]



if __name__ == '__main__':
    # 记得改线路号！！！！！！！！！！！！！
    creat_station_cmd(stations, '广佛线', 1, False,[])
