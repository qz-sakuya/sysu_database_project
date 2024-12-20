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


stations =[
    "浔峰岗", "横沙", "沙贝", "河沙", "坦尾", "如意坊", "黄沙", "文化公园", "一德路", "海珠广场", "北京路",
    "团一大广场", "东湖", "东山口", "区庄", "黄花岗", "沙河顶", "天平架", "燕塘", "天河客运站", "长湴",
    "植物园", "龙洞", "柯木塱", "高塘石", "黄陂", "金峰", "暹岗", "苏元", "萝岗", "香雪"
]



if __name__ == '__main__':
    # 记得改线路号！！！！！！！！！！！！！
    creat_station_cmd(stations, '6号线', 1, False,[18])
