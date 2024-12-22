# application01/views.py
from operator import itemgetter

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

# views.py
from django.shortcuts import render
from django.core.management.base import BaseCommand, CommandError
import base64

from application01.models import Line, Platform, Station, Exit, Section, Transfer, FirstTrain, LastTrain, \
    StationFacility, Image

from django.core.exceptions import ObjectDoesNotExist
import base64
from django.db.models import FloatField, Max, Q
from django.db.models.functions import Cast

from collections import defaultdict
import heapq


# 初始视图
def index(request):
    lines = Line.objects.annotate(
        line_no_float=Cast('line_no', FloatField())
    ).order_by('line_no_float')  # 转为浮点数排序
    line_data = []

    # 创建一个线路到终点站的字典
    line_endpoints = {}

    # 获取每条线路的起终点站
    for line in lines:
        if line.line_no not in line_endpoints:
            platforms = Platform.objects.filter(line=line.id).order_by('platform_no')
            if platforms.exists():
                min_platform = platforms.first()
                max_platform = platforms.last()
                line_endpoints[line.line_no] = {
                    'min_station_name': min_platform.station.station_name,
                    'max_station_name': max_platform.station.station_name
                }
            else:
                line_endpoints[line.line_no] = {
                    'min_station_name': '',
                    'max_station_name': ''
                }

    for line in lines:
        if line.line_no in ['3.5', '14.5']:
            continue
        line.end_stations = [line_endpoints[line.line_no]]  # 添加起终点站信息

        # 3和3北，14和14支线合并储存终点站
        if line.line_no == '3':
            line.end_stations.append(line_endpoints['3.5'])
        elif line.line_no == '14':
            line.end_stations.append(line_endpoints['14.5'])

        # 100-200代表广佛线和佛山地铁，替换为实际编号
        if line.line_no == '100':
            line.line_no = 'GF'

        line_data.append(line)

    context = {
        'lines': line_data,
    }
    return render(request, 'application01/index.html', context)


# 显示线路图
def show_line_map(request):
    return render(request, 'application01/line_map.html')


def get_line_map(request):
    try:
        line_map_image = Image.objects.get(image_name="line-map")
        response = HttpResponse(line_map_image.image_data, content_type='image/jpg')
        return response
    except Image.DoesNotExist:
        # 如果没有图片，则返回404错误
        return HttpResponse("Image not found", status=404)


# 显示车站列表
def get_stations(stations, current_line=None):
    # 创建一个线路到终点站的字典
    line_endpoints = {}

    # 获取每个车站的所有相关信息
    station_list = []
    for station in stations:

        # 获取车站具有的站台和线路
        have_platforms = Platform.objects.filter(station=station)
        have_lines = Line.objects.filter(platform__in=have_platforms).distinct()

        # 更新线路到终点站的字典
        for line in have_lines:
            if line.id not in line_endpoints:
                platforms = Platform.objects.filter(line=line).order_by('platform_no')

                if platforms.exists():
                    min_platform = platforms.first()
                    max_platform = platforms.last()

                    # 获取车站名称并处理特殊情况
                    min_station_name = min_platform.station.station_name
                    max_station_name = max_platform.station.station_name

                    # 机场北文本缩短
                    if max_station_name == "机场北（2号航站楼）":
                        max_station_name = "机场北"

                    line_endpoints[line.id] = {
                        'min_station_name': min_station_name,
                        'max_station_name': max_station_name
                    }
                else:
                    line_endpoints[line.id] = {
                        'min_station_name': '',
                        'max_station_name': ''
                    }

        # 对线路数据进行处理
        # 首先转为字典
        lines_data = [
            {
                'id': line.id,
                'colour': line.colour,
                'line_no': line.line_no,
            }
            for line in have_lines
        ]

        # 按浮点数排序，并将当前查询的线路提前
        if current_line:
            lines_data.sort(key=lambda x: (x['line_no'] != current_line.line_no, float(x['line_no'])))

        # 修正3北、14支、广佛线线路编号
        for line in lines_data:
            if line['line_no'] == '3.5':
                line['line_no'] = '3'
            if line['line_no'] == '14.5':
                line['line_no'] = '14'
            if line['line_no'] == '100':
                line['line_no'] = 'GF'
        seen = set()  # 去重
        unique_lines_data = []
        for line in lines_data:
            key = line['line_no']
            if key not in seen:
                seen.add(key)
                unique_lines_data.append(line)
        lines_data = unique_lines_data

        # 获取车站的设施信息
        facilities = StationFacility.objects.filter(station=station).select_related('icon_image').order_by(
            '-facility_type')

        facility_data = [
            {
                'facility_type': facility.facility_type,
                'icon_image_data': base64.b64encode(facility.icon_image.image_data).decode(
                    'utf-8') if facility.icon_image else None
            }
            for facility in facilities
        ]

        # 获取车站的首末班车数据
        first_trains_data = []
        last_trains_data = []
        for plat in have_platforms:

            first_train = FirstTrain.objects.filter(platform=plat)
            for train in first_train:
                if train.direction == 'up':
                    direction_name = line_endpoints[plat.line_id]['max_station_name'] or '上行'
                else:
                    direction_name = line_endpoints[plat.line_id]['min_station_name'] or '下行'
                departure_time_str = train.departure_time.strftime('%H:%M') if train.departure_time else None
                first_trains_data.append({
                    'direction': direction_name,
                    'departure_time': departure_time_str
                })

            last_train = LastTrain.objects.filter(platform=plat)  # 假设LastTrain模型存在
            for train in last_train:
                if train.direction == 'up':
                    direction_name = line_endpoints[plat.line_id]['max_station_name'] or '上行'
                else:
                    direction_name = line_endpoints[plat.line_id]['min_station_name'] or '下行'
                departure_time_str = train.departure_time.strftime('%H:%M') if train.departure_time else None
                last_trains_data.append({
                    'direction': direction_name,
                    'departure_time': departure_time_str
                })

        station_list.append({
            'name': station.station_name,
            'lines': lines_data,
            'facilities': facility_data,
            'first_trains': first_trains_data,
            'last_trains': last_trains_data
        })
    return station_list


# 点击线路列表显示车站
def get_stations_for_line(request, line_no):
    if request.method == 'GET':
        try:
            # 将实际编号转为数字
            if line_no == 'GF':
                line_no = '100'

            current_line = Line.objects.get(line_no=line_no)
            platforms = Platform.objects.filter(line=current_line).order_by('-platform_no')

            stations = []
            for platform in platforms:
                stations.append(platform.station)

            station_list = get_stations(stations, current_line)
            return JsonResponse({'stations': station_list})
        except Line.DoesNotExist:
            return JsonResponse({'error': 'Line not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


# 搜索车站
def get_stations_for_search(request):
    if request.method == 'GET':
        search_text = request.GET.get('search_text', '').strip()

        try:
            # 根据提供的搜索文本进行模糊匹配查询
            stations = Station.objects.filter(
                station_name__icontains=search_text
            ).distinct()

            # 如果没有提供搜索文本或未找到任何车站，则返回空列表
            if not search_text or not stations.exists():
                return JsonResponse({'stations': []})

            station_list = get_stations(list(stations))

            return JsonResponse({'stations': station_list})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


# 计算路径
def calculate_path(request, start_station_name, end_station_name, search_type):
    if request.method == 'GET':
        try:
            # 获取起点站和终点站
            try:
                start_station = Station.objects.get(station_name=start_station_name)
            except ObjectDoesNotExist:
                return JsonResponse({'error': f'未找到名为 "{start_station_name}" 的起点站'}, status=400)

            try:
                end_station = Station.objects.get(station_name=end_station_name)
            except ObjectDoesNotExist:
                return JsonResponse({'error': f'未找到名为 "{end_station_name}" 的终点站'}, status=400)

            start_platforms = Platform.objects.filter(station=start_station)
            end_platforms = Platform.objects.filter(station=end_station)

            # 构建图并加入超级源点和超级汇点
            if search_type == '最短时间':
                graph, super_source_id, super_sink_id = build_graph_min_time(start_platforms, end_platforms)
            else:
                graph, super_source_id, super_sink_id = build_graph_min_transfer(start_platforms, end_platforms)

            # 使用Dijkstra算法计算最短路径
            path_ids = dijkstra(graph, super_source_id, super_sink_id)

            # 解析路径以统计车站数、换乘数等信息
            result = parse_path(path_ids, super_source_id, super_sink_id)

            # 由于数据来源不准的临时修正
            result['total_time'] = int(result['total_time'] * 1.2)

            return JsonResponse({
                'total_time': result['total_time'],
                'station_count': result['station_count'],
                'transfer_count': result['transfer_count'],
                'path': result['path']
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


def build_graph_min_time(start_platforms, end_platforms):
    graph = defaultdict(list)

    # 为超级源点和超级汇点分配id
    max_id = Platform.objects.aggregate(Max('id'))['id__max'] or 0
    super_source_id = max_id + 1
    super_sink_id = max_id + 2

    # 添加超级源点到所有起点站台的边（成本为0）
    for platform in start_platforms:
        graph[super_source_id].append((platform.id, 0))
        graph[platform.id].append((super_source_id, 0))

    # 添加超级汇点从所有终点站台的边（成本为0）
    for platform in end_platforms:
        graph[platform.id].append((super_sink_id, 0))
        graph[super_sink_id].append((platform.id, 0))

    # 构建实际的图结构
    for section in Section.objects.select_related('platform1', 'platform2').all():
        graph[section.platform1.id].append((section.platform2.id, section.travel_time))
        graph[section.platform2.id].append((section.platform1.id, section.travel_time))

    for transfer in Transfer.objects.select_related('platform1', 'platform2').all():
        graph[transfer.platform1.id].append((transfer.platform2.id, transfer.transfer_time))
        graph[transfer.platform2.id].append((transfer.platform1.id, transfer.transfer_time))

    return graph, super_source_id, super_sink_id


def build_graph_min_transfer(start_platforms, end_platforms):
    graph = defaultdict(list)

    # 为超级源点和超级汇点分配id
    max_id = Platform.objects.aggregate(Max('id'))['id__max'] or 0
    super_source_id = max_id + 1
    super_sink_id = max_id + 2

    # 添加超级源点到所有起点站台的边（成本为0）
    for platform in start_platforms:
        graph[super_source_id].append((platform.id, 0))
        graph[platform.id].append((super_source_id, 0))

    # 添加超级汇点从所有终点站台的边（成本为0）
    for platform in end_platforms:
        graph[platform.id].append((super_sink_id, 0))
        graph[super_sink_id].append((platform.id, 0))

    # 构建实际的图结构
    for section in Section.objects.select_related('platform1', 'platform2').all():
        graph[section.platform1.id].append((section.platform2.id, 0.001))
        graph[section.platform2.id].append((section.platform1.id, 0.001))

    for transfer in Transfer.objects.select_related('platform1', 'platform2').all():
        graph[transfer.platform1.id].append((transfer.platform2.id, 1))
        graph[transfer.platform2.id].append((transfer.platform1.id, 1))

    return graph, super_source_id, super_sink_id


def dijkstra(graph, start, end):
    queue = [(0, start, [])]
    visited = set()

    while queue:
        (cost, current, path) = heapq.heappop(queue)

        if current not in visited:
            visited.add(current)
            path = path + [current]

            if current == end:
                return path

            for neighbor, time_cost in graph[current]:
                if neighbor not in visited:
                    heapq.heappush(queue, (cost + time_cost, neighbor, path))

    return []


def parse_path(path_ids, super_source_id, super_sink_id):
    result = {
        'station_count': 0,
        'transfer_count': 0,
        'path': [],
        'total_time': 0
    }
    prev_platform = None
    prev_line = None
    take_count = 0

    # 创建一个线路到终点站的字典
    line_endpoints = {}

    for i, node in enumerate(path_ids):
        if node == super_source_id or node == super_sink_id:
            continue  # 忽略超级源点和超级汇点

        platform = Platform.objects.get(id=node)
        line = Line.objects.get(id=platform.line_id)

        # 更新线路终点站字典
        if line.id not in line_endpoints:
            platforms = Platform.objects.filter(line=line).order_by('platform_no')

            if platforms.exists():
                min_platform = platforms.first()
                max_platform = platforms.last()
                line_endpoints[line.id] = {
                    'min_station_name': min_platform.station.station_name,
                    'max_station_name': max_platform.station.station_name
                }
            else:
                line_endpoints[line.id] = {
                    'min_station_name': '',
                    'max_station_name': ''
                }

        # 修正3北、14支、广佛线线路编号
        if line.line_no == '3.5':
            line.line_no = '3'
        if line.line_no == '14.5':
            line.line_no = '14'
        if line.line_no == '100':
            line.line_no = 'GF'

        # 处理起点站
        if prev_platform is None:
            result['path'].append(
                {'text': platform.station.station_name, 'line_no': line.line_no, 'colour': line.colour})

        if prev_platform and prev_platform.line_id != platform.line_id:  # 换乘
            result['transfer_count'] += 1
            # 增加换乘时间
            transfer = Transfer.objects.filter(
                Q(platform1_id=prev_platform.id, platform2_id=platform.id) |
                Q(platform1_id=platform.id, platform2_id=prev_platform.id)).first()
            if transfer:
                result['total_time'] += transfer.transfer_time

            # 上一条线路的站数和末站
            result['path'].append({'text': f"（共{take_count}站）", 'line_no': "站数", 'colour': prev_line.colour})
            result['path'].append(
                {'text': prev_platform.station.station_name, 'line_no': prev_line.line_no, 'colour': prev_line.colour})

            # 换乘信息
            next_platform_id = path_ids[i + 1] if i + 1 < len(path_ids) else None
            next_platform = Platform.objects.get(id=next_platform_id)
            if next_platform.platform_no > platform.platform_no:
                direction_name = line_endpoints[platform.line_id]['max_station_name'] or '上行'
            else:
                direction_name = line_endpoints[platform.line_id]['min_station_name'] or '下行'
            transfer_text = f"换乘 {line.line_name} {direction_name} 方向"

            # 3号线直通车特判
            if platform.station.station_name == "体育西路":
                prev_prev_platform_id = path_ids[i - 2] if i >= 2 else None
                prev_prev_platform = Platform.objects.get(id=prev_prev_platform_id) if prev_prev_platform_id else None
                if prev_prev_platform and next_platform:
                    prev_prev_station_name = prev_prev_platform.station.station_name
                    next_station_name = next_platform.station.station_name
                    print(prev_prev_station_name, next_station_name)
                    if {'林和西', '珠江新城'} == {prev_prev_station_name, next_station_name}:
                        transfer_text += "，或搭乘南北直通车"

            result['path'].append({'text': transfer_text, 'line_no': "换乘", 'colour': "#999"})

            # 当前线路的首站
            result['path'].append(
                {'text': platform.station.station_name, 'line_no': line.line_no, 'colour': line.colour})
            take_count = 0
        else:
            result['station_count'] += 1
            # 增加区间时间
            if prev_platform:
                section = Section.objects.filter(
                    Q(platform1_id=prev_platform.id, platform2_id=platform.id) |
                    Q(platform1_id=platform.id, platform2_id=prev_platform.id)).first()
                if section:
                    result['total_time'] += section.travel_time

        prev_platform = platform
        prev_line = line
        take_count += 1

    # 处理终点站
    result['path'].append({'text': f"（共{take_count}站）", 'line_no': "站数", 'colour': prev_line.colour})
    result['path'].append(
        {'text': prev_platform.station.station_name, 'line_no': prev_line.line_no, 'colour': prev_line.colour})

    return result


# 显示车站信息页面
def show_station_info(request, station_name):
    if request.method == 'GET':
        try:
            # 获取指定名称的车站对象
            station = Station.objects.get(station_name=station_name)
        except Station.DoesNotExist:
            return HttpResponse("车站不存在", status=404)

        context = {
            'station_name': station.station_name,
        }

        return render(request, 'application01/station_info.html', context)
    else:
        return HttpResponse(status=405)


def get_station_info(request, station_name):
    if request.method == 'GET':
        try:
            # 获取指定名称的车站对象
            station = Station.objects.get(station_name=station_name)

            line_endpoints = {}

            # 获取车站具有的站台和线路
            have_platforms = Platform.objects.filter(station=station)
            have_lines = Line.objects.filter(platform__in=have_platforms).distinct()

            # 更新线路到终点站的字典
            for line in have_lines:
                if line.id not in line_endpoints:
                    platforms = Platform.objects.filter(line=line).order_by('platform_no')

                    if platforms.exists():
                        min_platform = platforms.first()
                        max_platform = platforms.last()

                        # 获取车站名称并处理特殊情况
                        min_station_name = min_platform.station.station_name
                        max_station_name = max_platform.station.station_name

                        line_endpoints[line.id] = {
                            'min_station_name': min_station_name,
                            'max_station_name': max_station_name
                        }
                    else:
                        line_endpoints[line.id] = {
                            'min_station_name': '',
                            'max_station_name': ''
                        }

            # 对线路数据进行处理
            # 首先转为字典
            lines_data = [
                {
                    'id': line.id,
                    'colour': line.colour,
                    'line_no': line.line_no,
                }
                for line in have_lines
            ]

            # 转为浮点数排序
            if lines_data:
                lines_data.sort(key=lambda x: float(x['line_no']))

            # 修正3北、14支、广佛线线路编号
            for line in lines_data:
                if line['line_no'] == '3.5':
                    line['line_no'] = '3'
                if line['line_no'] == '14.5':
                    line['line_no'] = '14'
                if line['line_no'] == '100':
                    line['line_no'] = 'GF'

            seen = set()  # 去重
            unique_lines_data = []
            for line in lines_data:
                key = line['line_no']
                if key not in seen:
                    seen.add(key)
                    unique_lines_data.append(line)
            lines_data = unique_lines_data

            # 获取车站的设施信息
            facilities = StationFacility.objects.filter(station=station).select_related('icon_image').order_by(
                '-facility_type')

            facility_data = [
                {
                    'facility_type': facility.facility_type,
                    'icon_image_data': base64.b64encode(facility.icon_image.image_data).decode(
                        'utf-8') if facility.icon_image else None
                }
                for facility in facilities
            ]

            # 获取车站的首末班车数据（按方向排列）
            trains_data = []
            for plat in have_platforms:
                # 获取线路信息
                line = Line.objects.filter(id=plat.line_id).values('id', 'colour', 'line_no', 'line_name').first()

                if line['line_no'] == '3.5':
                    line['line_no'] = '3'
                if line['line_no'] == '14.5':
                    line['line_no'] = '14'
                if line['line_no'] == '100':
                    line['line_no'] = 'GF'

                for direction in ['up', 'down']:  # 两个方向都要添加
                    direction_name = line_endpoints[plat.line_id].get(f'max_station_name') if direction == 'up' else \
                        line_endpoints[plat.line_id].get(f'min_station_name')
                    # 方向为本站则跳过
                    if direction_name == station_name:
                        continue

                    # 获取首班车时间
                    first_train = FirstTrain.objects.filter(platform=plat, direction=direction).first()
                    first_train_time = first_train.departure_time.strftime(
                        '%H:%M') if first_train and first_train.departure_time else '--'

                    # 获取末班车时间
                    last_train = LastTrain.objects.filter(platform=plat, direction=direction).first()
                    last_train_time = last_train.departure_time.strftime(
                        '%H:%M') if last_train and last_train.departure_time else '--'

                    # 将信息添加到列表中
                    trains_data.append({
                        'line_no': line['line_no'],
                        'line_name': line['line_name'],
                        'colour': line['colour'],
                        'direction': direction_name,
                        'first_train_time': first_train_time,
                        'last_train_time': last_train_time
                    })

            # 获取车站的出口信息
            exits = Exit.objects.filter(station=station)

            exit_data = [
                {
                    'exit_no': station_exit.exit_no,
                    'exit_name': station_exit.exit_name,
                    'exit_address': station_exit.exit_address,
                    'exit_sub_address': station_exit.exit_sub_address
                }
                for station_exit in exits
            ]

            station_data = {
                'name': station.station_name,
                'lines': lines_data,
                'facilities': facility_data,
                'trains': trains_data,
                'exits': exit_data
            }

            return JsonResponse(station_data)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
