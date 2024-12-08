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


# 初始视图
def index(request):
    lines = Line.objects.order_by('line_no')
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

    # 绑定起终点站信息
    for line in lines:
        if line.line_no in ['3.5', '14.5']:
            continue
        line.end_stations = [line_endpoints[line.line_no]]

        # 3和3北，14和14支线合并储存
        if line.line_no == '3':
            line.end_stations.append(line_endpoints['3.5'])
        elif line.line_no == '14':
            line.end_stations.append(line_endpoints['14.5'])

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

        # 将当前查询的线路提前
        if current_line:
            lines_data.sort(key=lambda x: (x['line_no'] != current_line.line_no, x['line_no']))

        # 修正3北和14支线路编号
        for line in lines_data:
            if line['line_no'] == '3.5':
                line['line_no'] = '3'
            if line['line_no'] == '14.5':
                line['line_no'] = '14'
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

        station_list.append({
            'name': station.station_name,
            'lines': lines_data,
            'facilities': facility_data,
            'first_trains': first_trains_data,
            'last_trains': last_trains_data
        })
    return station_list


def get_stations_for_line(request, line_no):
    if request.method == 'GET':
        try:
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
